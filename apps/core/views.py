from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from operations.models import DailyRecord, Category


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        active_shift = DailyRecord.objects.filter(user=user, is_active=True).first()
        context["active_shift"] = active_shift

        qs = DailyRecord.objects.filter(user=user)
        aggregates = qs.aggregate(
            total_inc=Sum("total_income"),
            total_cost=Sum("total_cost"),
            total_km=Sum(F("end_km") - F("start_km")),
        )

        income = aggregates["total_inc"] or 0
        cost = aggregates["total_cost"] or 0
        km = aggregates["total_km"] or 0

        cost_per_km = (cost / km) if km > 0 else 0
        income_per_km = (income / km) if km > 0 else 0

        context["kpis"] = {
            "income": income,
            "cost": cost,
            "profit": income - cost,
            "km": km,
            "cost_per_km": cost_per_km,
            "income_per_km": income_per_km,
        }

        context["recent_records"] = qs.order_by("-date")[:5]
        context['income_categories'] = Category.objects.filter(user=self.request.user, type="INCOME")
        context['cost_categories'] = Category.objects.filter(user=self.request.user, type="COST")

        return context
