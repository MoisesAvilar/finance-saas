import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from operations.models import DailyRecord, Maintenance, Transaction


class MonthlyReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        records_qs = (
            DailyRecord.objects.filter(user=user)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                total_income=Sum("total_income"),
                days=Count("id"),
                total_km=Sum(F("end_km") - F("start_km")),
            )
            .order_by("-month")
        )

        ops_qs = (
            Transaction.objects.filter(
                record__user=user, type="COST", category__is_maintenance=False
            )
            .annotate(month=TruncMonth("record__date"))
            .values("month")
            .annotate(op_cost=Sum("amount"))
        )
        ops_dict = {item["month"]: item["op_cost"] for item in ops_qs}

        maint_qs = (
            Maintenance.objects.filter(user=user)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(maint_cost=Sum("cost"))
        )
        maint_dict = {item["month"]: item["maint_cost"] for item in maint_qs}

        data = []
        for item in records_qs:
            month_date = item["month"]

            op_cost = ops_dict.get(month_date, 0)
            maintenance_cost = maint_dict.get(month_date, 0)

            total_income = item["total_income"] or 0
            total_km = item["total_km"] or 0

            total_cost_real = op_cost + maintenance_cost
            profit = total_income - total_cost_real

            income_per_km = total_income / total_km if total_km > 0 else 0
            cost_per_km = total_cost_real / total_km if total_km > 0 else 0
            profit_per_km = profit / total_km if total_km > 0 else 0

            data.append(
                {
                    "month": month_date.strftime("%Y-%m"),
                    "days_worked": item["days"],
                    "km_driven": total_km,
                    "financial": {
                        "income": total_income,
                        "cost": total_cost_real,
                        "operational_cost": op_cost,
                        "maintenance_cost": maintenance_cost,
                        "profit": profit,
                    },
                    "efficiency": {
                        "income_per_km": round(income_per_km, 2),
                        "cost_per_km": round(cost_per_km, 2),
                        "profit_per_km": round(profit_per_km, 2),
                    },
                }
            )

        return Response(data)


class ExportReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_pro:
            return Response({"detail": "Recurso exclusivo PRO"}, status=403)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="relatorio_financeiro.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            ["Data", "Veículo", "KM Inicial", "KM Final", "Receita", "Custos", "Lucro"]
        )

        records = DailyRecord.objects.filter(user=request.user).order_by("-date")
        for r in records:
            writer.writerow(
                [
                    r.date,
                    r.vehicle.model_name,
                    r.start_km,
                    r.end_km,
                    r.total_income,
                    r.total_cost,
                    r.profit,
                ]
            )

        return response
