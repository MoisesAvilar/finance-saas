from rest_framework import viewsets, permissions, filters, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError

from .models import Category, DailyRecord, Transaction, Maintenance
from vehicles.models import Vehicle
from .serializers import (
    CategorySerializer,
    DailyRecordSerializer,
    TransactionSerializer,
    MaintenanceSerializer,
    DailyRecordDetailSerializer,
)


class OnboardUserView(views.APIView):
    """
    Cria categorias padrão baseadas no perfil do usuário (App vs Entregas).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        types = request.data.get("types", [])
        user = request.user

        cats_to_create = [
            Category(
                user=user,
                name="Abastecimento",
                type="COST",
                color="#ef4444",
                is_fuel=True,
            ),
            Category(
                user=user,
                name="Manutenção",
                type="COST",
                color="#f97316",
                is_maintenance=True,
            ),
            Category(user=user, name="Alimentação", type="COST", color="#eab308"),
            Category(user=user, name="IPVA/Doc", type="COST", color="#64748b"),
            Category(user=user, name="Outros", type="COST", color="#94a3b8"),
        ]

        if "passenger" in types:
            cats_to_create.extend(
                [
                    Category(user=user, name="Uber", type="INCOME", color="#000000"),
                    Category(user=user, name="99", type="INCOME", color="#eab308"),
                    Category(user=user, name="Indrive", type="INCOME", color="#16a34a"),
                    Category(
                        user=user, name="Particular", type="INCOME", color="#059669"
                    ),
                ]
            )

        if "delivery" in types:
            cats_to_create.extend(
                [
                    Category(user=user, name="iFood", type="INCOME", color="#ea1d2c"),
                    Category(
                        user=user, name="Mercado Livre", type="INCOME", color="#ffe600"
                    ),
                    Category(user=user, name="Loggi", type="INCOME", color="#3b82f6"),
                    Category(user=user, name="Borzo", type="INCOME", color="#8b5cf6"),
                ]
            )

        if cats_to_create:
            Category.objects.bulk_create(cats_to_create)

        return Response({"status": "ok", "created": len(cats_to_create)})


class GetLastKmView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, vehicle_id):
        last_record = (
            DailyRecord.objects.filter(
                user=request.user, vehicle_id=vehicle_id, end_km__isnull=False
            )
            .order_by("-date", "-created_at")
            .first()
        )

        if last_record:
            return Response(
                {
                    "km": last_record.end_km,
                    "source": "last_shift",
                    "message": f"Último fechamento: {last_record.end_km} km",
                }
            )

        vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)
        start_km = getattr(vehicle, "current_odometer", vehicle.initial_km)

        return Response(
            {
                "km": start_km,
                "source": "vehicle_register",
                "message": f"Sugerido do cadastro: {start_km} km",
            }
        )


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DailyRecordViewSet(viewsets.ModelViewSet):
    serializer_class = DailyRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_active", "vehicle"]
    ordering_fields = ["date"]
    ordering = ["-date"]

    def get_queryset(self):
        qs = DailyRecord.objects.filter(user=self.request.user)

        if not self.request.user.is_pro:
            limit_date = timezone.now().date() - timedelta(days=30)
            qs = qs.filter(date__gte=limit_date)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DailyRecordDetailSerializer
        return DailyRecordSerializer

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Retorna o plantão ativo do usuário para o Header/Dashboard."""
        active_shift = DailyRecord.objects.filter(
            user=request.user, is_active=True
        ).first()
        if active_shift:
            serializer = self.get_serializer(active_shift)
            return Response(serializer.data)
        return Response(None)

    def perform_create(self, serializer):
        if DailyRecord.objects.filter(user=self.request.user, is_active=True).exists():
            raise ValidationError({"detail": "Você já tem um plantão em aberto."})

        hoje = timezone.now().date()
        if DailyRecord.objects.filter(user=self.request.user, date=hoje).exists():
            raise ValidationError({"detail": "Você já abriu um plantão hoje."})

        serializer.save(user=self.request.user, date=hoje, is_active=True)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["record", "type", "category"]

    def get_queryset(self):
        return Transaction.objects.filter(record__user=self.request.user).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        instance = serializer.save()

        if instance.type == "COST" and instance.category.is_maintenance:
            final_odometer = instance.actual_km
            if not final_odometer:
                final_odometer = instance.record.end_km or instance.record.start_km

            Maintenance.objects.create(
                user=self.request.user,
                vehicle=instance.record.vehicle,
                date=instance.record.date,
                cost=instance.amount,
                odometer=final_odometer,
                type="OTHER",
                description=f"Via Dashboard: {instance.description or instance.category.name}",
                transaction=instance,
                next_due_km=instance.next_due_km,
            )

    def perform_update(self, serializer):
        instance = serializer.save()
        
        if hasattr(instance, 'maintenance_mirror'):
            maint = instance.maintenance_mirror.first()
            
            if maint:
                maint.cost = instance.amount
                maint.description = f"Via Dashboard: {instance.description or instance.category.name}"
                
                if instance.actual_km:
                    maint.odometer = instance.actual_km
                    
                if instance.next_due_km:
                    maint.next_due_km = instance.next_due_km
                    
                maint.save()


class MaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ["-date"]

    def get_queryset(self):
        return Maintenance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
