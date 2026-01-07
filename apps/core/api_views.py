from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, F
from django.utils import timezone
from operations.models import DailyRecord, Category
from .serializers import (
    DashboardCategorySerializer,
    DashboardRecordSerializer,
    ActiveShiftSerializer,
)
from vehicles.models import Vehicle


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        records_qs = DailyRecord.objects.filter(
            user=user, date__month=current_month, date__year=current_year
        )

        aggregates = records_qs.aggregate(
            total_inc=Sum("total_income"),
            total_cost=Sum("total_cost"),
            total_km=Sum(F("end_km") - F("start_km")),
        )

        income = aggregates["total_inc"] or 0
        cost = aggregates["total_cost"] or 0
        km = aggregates["total_km"] or 0
        profit = income - cost

        income_per_km = (income / km) if km > 0 else 0
        cost_per_km = (cost / km) if km > 0 else 0

        active_shift = DailyRecord.objects.filter(user=user, is_active=True).first()
        active_shift_data = (
            ActiveShiftSerializer(active_shift).data if active_shift else None
        )

        current_vehicle = (
            active_shift.vehicle
            if active_shift
            else Vehicle.objects.filter(user=user, is_active=True).first()
        )

        vehicle_stats = {"fuel_avg": 0, "maintenance": None}

        if current_vehicle:
            vehicle_stats["fuel_avg"] = current_vehicle.fuel_average or 0
            vehicle_stats["maintenance"] = current_vehicle.maintenance_status

        income_cats = Category.objects.filter(user=user, type="INCOME")
        cost_cats = Category.objects.filter(user=user, type="COST")
        recent_records = DailyRecord.objects.filter(
            user=user, is_active=False
        ).order_by("-date")[:5]

        last_7_days = DailyRecord.objects.filter(user=user).order_by("-date")[:7]
        chart_data = []
        for rec in reversed(last_7_days):
            rec_profit = rec.total_income - rec.total_cost
            chart_data.append(
                {"date": rec.date.strftime("%d/%m"), "profit": rec_profit}
            )

        return Response(
            {
                "period": f"{now.strftime('%B')}/{current_year}",
                "kpi": {
                    "income": income,
                    "cost": cost,
                    "profit": profit,
                    "km_driven": km,
                    "income_per_km": round(income_per_km, 2),
                    "cost_per_km": round(cost_per_km, 2),
                },
                "vehicle_stats": vehicle_stats,
                "active_shift": active_shift_data,
                "lists": {
                    "recent_records": DashboardRecordSerializer(
                        recent_records, many=True
                    ).data,
                    "income_categories": DashboardCategorySerializer(
                        income_cats, many=True
                    ).data,
                    "cost_categories": DashboardCategorySerializer(
                        cost_cats, many=True
                    ).data,
                },
                "chart_data": chart_data,
            }
        )


class PricingInfoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        pricing_info = {
            "free_tier": {
                "max_daily_records": 10,
                "max_vehicles": 1,
                "support": "Email support",
            },
            "pro_tier": {
                "max_daily_records": "Unlimited",
                "max_vehicles": "Unlimited",
                "support": "Priority email support",
            },
        }
        return Response(pricing_info)
