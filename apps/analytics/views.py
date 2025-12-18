from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth
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
                income=Sum("total_income"),
                op_cost=Sum("total_cost"),
                km=Sum(F("end_km") - F("start_km")),
                days=Count("id"),
            )
        )

        maint_qs = (
            Maintenance.objects.filter(user=user)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(maint_cost=Sum("cost"))
        )

        report_data = {}

        for item in daily_qs:
            month = item["month"]
            report_data[month] = {
                "month": month,
                "income": item["income"] or 0,
                "op_cost": item["op_cost"] or 0,
                "maint_cost": 0,
                "km": item["km"] or 0,
                "days": item["days"],
            }

        for item in maint_qs:
            month = item["month"]
            if month not in report_data:
                report_data[month] = {
                    "month": month,
                    "income": 0,
                    "op_cost": 0,
                    "maint_cost": 0,
                    "km": 0,
                    "days": 0,
                }
            report_data[month]["maint_cost"] = item["maint_cost"] or 0

        final_report = []
        for month, data in report_data.items():
            total_cost = data["op_cost"] + data["maint_cost"]
            profit = data["income"] - total_cost

            km = data["km"] or 1
            cost_per_km = total_cost / km

            data["total_cost"] = total_cost
            data["profit"] = profit
            data["cost_per_km"] = cost_per_km

            final_report.append(data)

        final_report.sort(key=lambda x: x["month"], reverse=True)

        context["report"] = final_report
        return context
