import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta, datetime
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
        today_date = now.date()

        try:
            target_month = int(request.query_params.get("month", now.month))
            target_year = int(request.query_params.get("year", now.year))
            base_date = now.replace(year=target_year, month=target_month, day=1).date()
        except ValueError:
            base_date = today_date
            target_month = now.month
            target_year = now.year

        first_day_month = base_date.replace(day=1)
        next_month = (base_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_month = next_month - timedelta(days=1)

        last_month_end = first_day_month - timedelta(days=1)
        first_day_last_month = last_month_end.replace(day=1)

        records_qs = DailyRecord.objects.filter(
            user=user, date__range=[first_day_month, last_day_month]
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

        def get_accumulated_data(start_date, end_date):
            recs = DailyRecord.objects.filter(
                user=user, date__range=[start_date, end_date]
            ).values("date", "total_income", "total_cost")

            daily_map = {
                r["date"].day: (r["total_income"] - r["total_cost"]) for r in recs
            }

            data = []
            accumulated = 0

            is_current_month = (
                end_date.month == today_date.month and end_date.year == today_date.year
            )
            limit_date = min(end_date, today_date) if is_current_month else end_date

            days_range = (limit_date - start_date).days + 1

            for i in range(1, days_range + 1):
                day_profit = daily_map.get(i, 0)
                accumulated += day_profit
                data.append({"day": i, "value": float(accumulated)})
            return data

        comparison_chart = {
            "current": get_accumulated_data(first_day_month, last_day_month),
            "last": get_accumulated_data(first_day_last_month, last_month_end),
        }

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

        month_records = records_qs.order_by("-date")

        return Response(
            {
                "period": f"{base_date.strftime('%B')}/{target_year}",
                "period_query": {"month": target_month, "year": target_year},
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
                        month_records, many=True
                    ).data,
                    "income_categories": DashboardCategorySerializer(
                        income_cats, many=True
                    ).data,
                    "cost_categories": DashboardCategorySerializer(
                        cost_cats, many=True
                    ).data,
                },
                "comparison_chart": comparison_chart,
            }
        )


class ExportReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_pro:
            return Response(
                {"detail": "Funcionalidade exclusiva para assinantes PRO."},
                status=status.HTTP_403_FORBIDDEN,
            )

        now = timezone.now()
        try:
            month = int(request.query_params.get("month", now.month))
            year = int(request.query_params.get("year", now.year))
        except ValueError:
            month = now.month
            year = now.year

        records = DailyRecord.objects.filter(
            user=request.user, date__month=month, date__year=year
        ).order_by("date")

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="relatorio_{month}_{year}.csv"'
            },
        )

        response.write("\ufeff".encode("utf8"))

        writer = csv.writer(
            response, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        writer.writerow(
            [
                "Data",
                "Veículo",
                "KM Rodado",
                "Receita (R$)",
                "Custo (R$)",
                "Lucro Líquido (R$)",
                "Situação",
            ]
        )

        for rec in records:
            writer.writerow(
                [
                    rec.date.strftime("%d/%m/%Y"),
                    rec.vehicle.model_name,
                    rec.km_driven,
                    str(rec.total_income).replace(".", ","),
                    str(rec.total_cost).replace(".", ","),
                    str(rec.profit).replace(".", ","),
                    "Em Aberto" if rec.is_active else "Fechado",
                ]
            )

        return response


class PricingInfoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "free_tier": {"desc": "Plano Gratuito"},
                "pro_tier": {"desc": "Plano Profissional"},
            }
        )
