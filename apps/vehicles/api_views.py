from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vehicle
from .serializers import VehicleSerializer, VehicleMaintenanceSerializer
from operations.models import Transaction, Maintenance


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user).order_by(
            "-is_active", "model_name"
        )

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_pro:
            count = Vehicle.objects.filter(user=user).count()
            if count >= 1:
                raise serializers.ValidationError(
                    {
                        "detail": "🔒 Limite atingido! No plano Grátis você pode ter apenas 1 veículo ativo."
                    }
                )

        serializer.save(user=user)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """
        Retorna dados detalhados para a dashboard do veículo.
        Substitui a lógica complexa que existia na VehicleDetailView.
        """
        vehicle = self.get_object()

        fuel_transactions = Transaction.objects.filter(
            record__vehicle=vehicle, category__is_fuel=True, liters__gt=0
        ).order_by("actual_km")

        fuel_history = []
        last_full_tank = None
        pending_liters = 0
        pending_cost = 0

        for trans in fuel_transactions:
            item = {
                "id": trans.id,
                "date": trans.created_at.strftime("%d/%m/%Y"),
                "km": trans.actual_km,
                "liters": float(trans.liters),
                "cost": float(trans.amount),
                "is_full": trans.is_full_tank,
                "avg": None,
                "cost_per_km": None,
            }

            if last_full_tank and trans.is_full_tank:
                km_driven = trans.actual_km - last_full_tank.actual_km
                total_liters_cycle = pending_liters + trans.liters
                total_cost_cycle = pending_cost + trans.amount

                if km_driven > 0 and total_liters_cycle > 0:
                    item["avg"] = round(km_driven / float(total_liters_cycle), 2)
                    item["cost_per_km"] = round(float(total_cost_cycle) / km_driven, 2)

                pending_liters = 0
                pending_cost = 0
                last_full_tank = trans

            elif trans.is_full_tank:
                last_full_tank = trans
                pending_liters = 0
                pending_cost = 0

            else:
                pending_liters += trans.liters
                pending_cost += trans.amount

            fuel_history.insert(0, item)

        maintenances = Maintenance.objects.filter(vehicle=vehicle).order_by("-date")
        maint_serializer = VehicleMaintenanceSerializer(maintenances, many=True)

        maint_stats = {}
        for m in maintenances:
            label = m.get_type_display()
            if label not in maint_stats:
                maint_stats[label] = 0
            maint_stats[label] += float(m.cost)

        maint_stats_list = [{"name": k, "total": v} for k, v in maint_stats.items()]

        return Response(
            {
                "fuel_history": fuel_history,
                "maintenances": maint_serializer.data,
                "maintenance_stats": maint_stats_list,
                "vehicle_data": VehicleSerializer(vehicle).data,
            }
        )
