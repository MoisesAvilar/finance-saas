from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, DailyRecord, Transaction, Maintenance
from .serializers import (
    CategorySerializer,
    DailyRecordSerializer,
    TransactionSerializer,
    MaintenanceSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

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
        return DailyRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["record", "type", "category"]

    def get_queryset(self):
        return Transaction.objects.filter(record__user=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()

        if instance.type == "COST" and instance.category.is_maintenance:
            final_odometer = (
                instance.actual_km
                if instance.actual_km
                else (instance.record.end_km or instance.record.start_km)
            )

            Maintenance.objects.create(
                user=self.request.user,
                vehicle=instance.record.vehicle,
                date=instance.record.date,
                cost=instance.amount,
                odometer=final_odometer,
                type="OTHER",
                description=f"Via App: {instance.description}"
                if instance.description
                else "Registro rápido via App",
                transaction=instance,
            )


class MaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ["-date"]

    def get_queryset(self):
        return Maintenance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
