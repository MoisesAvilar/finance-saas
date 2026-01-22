from rest_framework import viewsets, permissions, filters, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from django.db.models import Sum, Q
from django.db import models
from rest_framework.views import APIView
from .models import Transaction, Category, DailyRecord, Maintenance
from datetime import datetime

from vehicles.models import Vehicle
from .serializers import (
    CategorySerializer,
    DailyRecordSerializer,
    TransactionSerializer,
    MaintenanceSerializer,
    DailyRecordDetailSerializer,
)


class MonthlyReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        view_type = request.query_params.get("view", "monthly")
        month = int(request.query_params.get("month", datetime.now().month))
        year = int(request.query_params.get("year", datetime.now().year))
        user = request.user

        # Filtros de tempo
        trans_filters = Q(record__user=user, record__date__year=year)
        record_filters = Q(user=user, date__year=year)

        if view_type == "monthly":
            trans_filters &= Q(record__date__month=month)
            record_filters &= Q(date__month=month)

        # 1. Cálculos de Totais
        transactions = Transaction.objects.filter(trans_filters)

        total_income = (
            transactions.filter(type="INCOME").aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        total_cost = (
            transactions.filter(type="COST").aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        # Apenas registros finalizados entram no cálculo de KM
        records = DailyRecord.objects.filter(record_filters, is_active=False)
        total_km = sum(r.km_driven for r in records)
        km_float = float(total_km) if total_km > 0 else 0

        # 2. Agrupamento por Categorias
        income_cats_qs = (
            transactions.filter(type="INCOME")
            .values("category__id", "category__name", "category__color")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        cost_cats_qs = (
            transactions.filter(type="COST")
            .values("category__id", "category__name", "category__color")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        # 3. Preparação do Histórico (Apenas para PRO)
        history_data = []
        if user.is_pro:
            if view_type == "monthly":
                history_qs = (
                    transactions.values("record__id", "record__date")
                    .annotate(
                        income=Sum("amount", filter=Q(type="INCOME")),
                        cost=Sum("amount", filter=Q(type="COST")),
                    )
                    .order_by("record__date")
                )
                for entry in history_qs:
                    history_data.append(
                        {
                            "id": entry["record__id"],
                            "date": entry["record__date"].strftime("%d/%m"),
                            "income": float(entry["income"] or 0),
                            "cost": float(entry["cost"] or 0),
                        }
                    )
            else:
                history_qs = (
                    transactions.values("record__date__month")
                    .annotate(
                        income=Sum("amount", filter=Q(type="INCOME")),
                        cost=Sum("amount", filter=Q(type="COST")),
                    )
                    .order_by("record__date__month")
                )
                labels = [
                    "Jan",
                    "Fev",
                    "Mar",
                    "Abr",
                    "Mai",
                    "Jun",
                    "Jul",
                    "Ago",
                    "Set",
                    "Out",
                    "Nov",
                    "Dez",
                ]
                for entry in history_qs:
                    history_data.append(
                        {
                            "date": labels[entry["record__date__month"] - 1],
                            "income": float(entry["income"] or 0),
                            "cost": float(entry["cost"] or 0),
                        }
                    )

        # 4. Montagem da Resposta com o "Pulo do Gato"
        return Response(
            {
                "is_pro": user.is_pro,
                "summary": {
                    "total_income": float(total_income),
                    "total_cost": float(total_cost),
                    "net_profit": float(total_income - total_cost),
                    "total_km": total_km,
                    # Métricas por KM do Resumo
                    "income_per_km": round(float(total_income) / km_float, 2)
                    if km_float > 0
                    else 0,
                    "cost_per_km": round(float(total_cost) / km_float, 2)
                    if km_float > 0
                    else 0,
                    "profit_per_km": round(
                        float(total_income - total_cost) / km_float, 2
                    )
                    if km_float > 0
                    else 0,
                },
                "income_categories": [
                    {
                        "id": c["category__id"],
                        "name": c["category__name"],
                        "color": c["category__color"],
                        "value": float(c["total"]),
                        "per_km": round(float(c["total"]) / km_float, 2)
                        if km_float > 0
                        else 0,
                        "percentage": round(
                            (float(c["total"]) / float(total_income) * 100), 1
                        )
                        if total_income > 0
                        else 0,
                    }
                    for c in income_cats_qs
                ],
                "cost_categories": [
                    {
                        "id": c["category__id"],
                        "name": c["category__name"],
                        "color": c["category__color"],
                        "value": float(c["total"]),
                        "per_km": round(float(c["total"]) / km_float, 2)
                        if km_float > 0
                        else 0,
                        "percentage": round(
                            (float(c["total"]) / float(total_cost) * 100), 1
                        )
                        if total_cost > 0
                        else 0,
                    }
                    for c in cost_cats_qs
                ],
                "daily_history": history_data,
            }
        )


class OnboardUserView(views.APIView):
    """
    Cria categorias DE RECEITA.
    Modo 1: Recebe 'types' e cria tudo daquele tipo.
    Modo 2: Recebe 'app_list' e cria apenas os apps específicos solicitados.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        types = request.data.get("types", [])
        app_list = request.data.get("app_list", None)
        user = request.user

        CATALOG = {
            # Passageiros
            "Uber": {"color": "#000000", "type": "passenger"},
            "99": {"color": "#eab308", "type": "passenger"},
            "Indrive": {"color": "#16a34a", "type": "passenger"},
            "Particular": {"color": "#059669", "type": "passenger"},
            "Black": {"color": "#111827", "type": "passenger"},
            # Entregas
            "iFood": {"color": "#ea1d2c", "type": "delivery"},
            "Mercado Livre": {"color": "#ffe600", "type": "delivery"},
            "Loggi": {"color": "#3b82f6", "type": "delivery"},
            "Borzo": {"color": "#8b5cf6", "type": "delivery"},
            "Zé Delivery": {"color": "#f59e0b", "type": "delivery"},
            "CornerShop": {"color": "#ef4444", "type": "delivery"},
        }

        wanted_cats = []

        if app_list is not None:
            for app_name in app_list:
                if app_name in CATALOG:
                    wanted_cats.append(
                        {"name": app_name, "color": CATALOG[app_name]["color"]}
                    )
        else:
            for name, data in CATALOG.items():
                if data["type"] in types:
                    wanted_cats.append({"name": name, "color": data["color"]})

        if not wanted_cats:
            wanted_cats.append({"name": "Ganhos Diversos", "color": "#059669"})

        existing_names = set(
            Category.objects.filter(user=user, type="INCOME").values_list(
                "name", flat=True
            )
        )

        cats_to_create = [
            Category(user=user, name=c["name"], type="INCOME", color=c["color"])
            for c in wanted_cats
            if c["name"] not in existing_names
        ]

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

        if hasattr(instance, "maintenance_mirror"):
            maint = instance.maintenance_mirror.first()

            if maint:
                maint.cost = instance.amount
                maint.description = (
                    f"Via Dashboard: {instance.description or instance.category.name}"
                )

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


class CategoryReportDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        month = request.query_params.get("month", datetime.now().month)
        year = request.query_params.get("year", datetime.now().year)
        user = request.user

        category = get_object_or_404(Category, pk=pk, user=user)

        transactions = Transaction.objects.filter(
            category=category, record__date__month=month, record__date__year=year
        ).order_by("-record__date")

        serializer = TransactionSerializer(transactions, many=True)
        category_data = CategorySerializer(category).data

        return Response(
            {
                "category": category_data,
                "total_period": transactions.aggregate(Sum("amount"))["amount__sum"] or 0,
                "count": transactions.count(),
                "transactions": serializer.data,
            }
        )
