from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.db import models
from operations.models import DailyRecord, Maintenance


class MonthlyPerformanceView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/monthly_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        daily_qs = (
            DailyRecord.objects.filter(user=user)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                total_income=Sum("total_income"),
                total_op_cost=Sum("total_cost"),
                total_km=Sum(F("end_km") - F("start_km")),
                days_count=models.Count("id"),
            )
            .order_by("-month")
        )

        maint_qs = (
            Maintenance.objects.filter(user=user)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_maint_cost=Sum("cost"))
            .order_by("-month")
        )

        maint_dict = {item["month"]: item["total_maint_cost"] for item in maint_qs}

        report_data = []

        for item in daily_qs:
            month = item["month"]
            income = item["total_income"] or 0
            op_cost = item["total_op_cost"] or 0
            km = item["total_km"] or 0

            maint_cost = maint_dict.get(month, 0)

            total_cost = op_cost + maint_cost
            profit = income - total_cost

            cost_per_km = (total_cost / km) if km > 0 else 0
            income_per_km = (income / km) if km > 0 else 0

            report_data.append(
                {
                    "month": month,
                    "days": item["days_count"],
                    "km": km,
                    "income": income,
                    "op_cost": op_cost,
                    "maint_cost": maint_cost,
                    "total_cost": total_cost,
                    "profit": profit,
                    "cost_per_km": cost_per_km,
                    "income_per_km": income_per_km,
                }
            )

        context["report"] = report_data
        return context
