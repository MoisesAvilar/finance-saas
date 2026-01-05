from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum
from django.utils import timezone
from operations.models import DailyRecord, Transaction


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        records = DailyRecord.objects.filter(
            user=user, date__month=current_month, date__year=current_year
        )

        income = records.aggregate(s=Sum("total_income"))["s"] or 0
        cost = records.aggregate(s=Sum("total_cost"))["s"] or 0

        # Recalcula lucro baseado nos aggregates para precisão
        profit = income - cost

        km_driven = 0
        for rec in records:
            km_driven += rec.km_driven

        # Busca plantão ativo
        active_shift = DailyRecord.objects.filter(user=user, is_active=True).first()
        active_shift_id = active_shift.id if active_shift else None

        # Dados para o gráfico simples (últimos 7 dias)
        last_7_days = DailyRecord.objects.filter(user=user).order_by("-date")[:7]
        chart_data = []
        for rec in reversed(last_7_days):
            chart_data.append(
                {"date": rec.date.strftime("%d/%m"), "profit": rec.profit}
            )

        return Response(
            {
                "period": f"{now.strftime('%B')}/{current_year}",
                "kpi": {
                    "income": income,
                    "cost": cost,
                    "profit": profit,
                    "km_driven": km_driven,
                },
                "active_shift_id": active_shift_id,
                "chart_data": chart_data,
            }
        )
