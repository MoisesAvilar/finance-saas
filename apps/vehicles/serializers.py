from rest_framework import serializers
from django.apps import apps
from django.db.models import Sum
from .models import Vehicle
from operations.models import Maintenance, DailyRecord, Transaction


class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Maintenance
        fields = [
            "id",
            "date",
            "formatted_date",
            "odometer",
            "cost",
            "type",
            "type_display",
            "description",
        ]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")


class VehicleSerializer(serializers.ModelSerializer):
    odometer = serializers.ReadOnlyField(source="current_odometer")
    fuel_average = serializers.ReadOnlyField()
    maintenance_status = serializers.ReadOnlyField()
    formatted_created_at = serializers.SerializerMethodField()

    stats = serializers.SerializerMethodField()
    consumption_history = serializers.SerializerMethodField()
    maintenance_history = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "model_name",
            "plate",
            "fuel_type",
            "initial_km",
            "is_active",
            "odometer",
            "fuel_average",
            "maintenance_status",
            "created_at",
            "formatted_created_at",
            "stats",
            "consumption_history",
            "maintenance_history",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate(self, data):
        """
        Implementa a lógica do 'Frozen Slot' para usuários FREE.
        """
        request = self.context.get("request")
        if not request or not request.user:
            return data

        user = request.user

        if getattr(user, "is_pro", False):
            return data

        if "is_active" in data:
            new_status = data["is_active"]

            if self.instance:
                current_status = self.instance.is_active

                if current_status is True and new_status is False:
                    raise serializers.ValidationError(
                        {
                            "is_active": "No plano Grátis, o slot de veículo é fixo. Para trocar de veículo, você deve fazer Upgrade ou EXCLUIR permanentemente o veículo atual."
                        }
                    )

                if new_status is True and current_status is False:
                    if (
                        Vehicle.objects.filter(user=user, is_active=True)
                        .exclude(pk=self.instance.pk)
                        .exists()
                    ):
                        raise serializers.ValidationError(
                            {
                                "is_active": "Você já tem um veículo ocupando seu slot gratuito. Assine o PRO para gerenciar múltiplos carros."
                            }
                        )

            else:
                if new_status is True:
                    if Vehicle.objects.filter(user=user, is_active=True).exists():
                        raise serializers.ValidationError(
                            {"is_active": "Limite de slot atingido."}
                        )

        return data

    def get_formatted_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")

    def validate_initial_km(self, value):
        if value < 0:
            raise serializers.ValidationError("A quilometragem não pode ser negativa.")
        return value

    def validate_plate(self, value):
        return value.upper().replace("-", "").strip() if value else value

    def validate_model_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "O nome do modelo deve ser mais descritivo (mínimo 3 caracteres)."
            )
        return value

    def get_stats(self, obj):
        total_maint = Maintenance.objects.filter(vehicle=obj).aggregate(Sum('cost'))['cost__sum'] or 0
        last_maint = Maintenance.objects.filter(vehicle=obj).order_by('-date').first()

        financial_data = DailyRecord.objects.filter(vehicle=obj).aggregate(
            total_earnings=Sum('total_income'),
            total_cost=Sum('total_cost')
        )
        earnings = float(financial_data['total_earnings'] or 0)
        costs = float(financial_data['total_cost'] or 0)
        profit = earnings - costs

        records = DailyRecord.objects.filter(vehicle=obj, is_active=False)
        total_km_history = sum((r.end_km - r.start_km) for r in records if r.end_km and r.start_km)

        last_tx_with_next_due = Transaction.objects.filter(
            record__vehicle=obj, 
            next_due_km__isnull=False
        ).order_by('-created_at').first()
        
        next_km = last_tx_with_next_due.next_due_km if last_tx_with_next_due else None

        return {
            "total_earnings": earnings,
            "total_cost": costs,
            "profit_total": profit,
            "profit_per_km": round(profit / total_km_history, 2) if total_km_history > 0 else 0,
            "days_active": records.count(),
            "total_km_history": total_km_history,
            "fuel_average": float(obj.fuel_average) if obj.fuel_average else 0,
            "total_maintenance": float(total_maint),
            "last_maintenance_date": last_maint.date if last_maint else None,
            "next_maintenance_km": next_km, # Agora vai enviar o valor correto (53914)
            "avg_daily_km": round(total_km_history / records.count(), 1) if records.count() > 0 else 0,
        }

    def get_consumption_history(self, obj):
        Transaction = apps.get_model("operations", "Transaction")

        txs = Transaction.objects.filter(
            record__vehicle=obj,
            category__is_fuel=True,
            actual_km__isnull=False,
            liters__isnull=False,
        ).order_by("actual_km")

        history = []
        tx_list = list(txs)

        for i in range(1, len(tx_list)):
            prev = tx_list[i - 1]
            curr = tx_list[i]

            km_diff = curr.actual_km - prev.actual_km

            if km_diff > 0 and curr.liters > 0:
                avg = km_diff / float(curr.liters)

                if 4 < avg < 70:
                    history.append(
                        {
                            "km": f"{curr.actual_km}km",
                            "media": round(avg, 1),
                            "date": curr.record.date.strftime("%d/%m"),
                        }
                    )

        return history[-6:]

    def get_maintenance_history(self, obj):
        maints = Maintenance.objects.filter(vehicle=obj).order_by("-date")[:5]

        data = []
        for m in maints:
            data.append(
                {
                    "id": m.id,
                    "description": m.description or m.get_type_display(),
                    "date": m.date.strftime("%d/%m/%Y"),
                    "km": m.odometer,
                    "amount": m.cost,
                }
            )
        return data
