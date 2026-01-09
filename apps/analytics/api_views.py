import xlsxwriter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from operations.models import DailyRecord, Maintenance, Transaction
from io import BytesIO


class ExportReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_pro:
            return Response(
                {"error": "Esta funcionalidade é exclusiva para usuários PRO."},
                status=status.HTTP_403_FORBIDDEN,
            )

        month = request.query_params.get("month")
        year = request.query_params.get("year")

        records = DailyRecord.objects.filter(
            user=user, date__month=month, date__year=year, is_active=False
        ).order_by("date")

        if not records.exists():
            return Response(
                {"error": "Nenhum dado encontrado para este período."}, status=404
            )

        transactions = Transaction.objects.filter(
            record__user=user, record__date__month=month, record__date__year=year
        )

        # CORREÇÃO AQUI: Filtrando pela Flag is_fuel e is_maintenance
        fuel_total = float(
            transactions.filter(category__is_fuel=True).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        maint_total = float(
            transactions.filter(category__is_maintenance=True).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        total_income = float(
            records.aggregate(Sum("total_income"))["total_income__sum"] or 0
        )

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        # Estilos
        header_fmt = workbook.add_format(
            {"bold": True, "bg_color": "#1e293b", "font_color": "white", "border": 1}
        )
        money_fmt = workbook.add_format({"num_format": "R$ #,##0.00", "border": 1})
        date_fmt = workbook.add_format({"num_format": "dd/mm/yyyy", "border": 1})
        border_fmt = workbook.add_format({"border": 1})
        bold_money_fmt = workbook.add_format(
            {"bold": True, "num_format": "R$ #,##0.00", "bg_color": "#f1f5f9"}
        )

        # Aba Histórico
        ws_hist = workbook.add_worksheet("Histórico Detalhado")
        headers = ["Data", "Ganhos", "Custos", "Lucro", "KM Rodados", "R$/KM"]
        for col, text in enumerate(headers):
            ws_hist.write(0, col, text, header_fmt)

        for row, r in enumerate(records, start=1):
            ws_hist.write(row, 0, r.date.strftime("%Y-%m-%d"), date_fmt)
            ws_hist.write(
                row, 1, float(r.total_income), money_fmt
            )  # Usando total_income correto
            ws_hist.write(
                row, 2, float(r.total_cost), money_fmt
            )  # Usando total_cost correto
            ws_hist.write(row, 3, float(r.profit), money_fmt)
            ws_hist.write(row, 4, float(r.km_driven), border_fmt)
            ws_hist.write(row, 5, float(r.income_per_km), money_fmt)

        ws_hist.set_column("A:F", 15)

        # Aba Fiscal
        ws_fiscal = workbook.add_worksheet("Resumo Fiscal")
        ws_fiscal.set_column("A:A", 40)
        ws_fiscal.set_column("B:B", 20)
        ws_fiscal.set_column("C:C", 50)

        fiscal_headers = ["Descrição", "Valor", "Nota para Carnê-Leão"]
        for col, text in enumerate(fiscal_headers):
            ws_fiscal.write(0, col, text, header_fmt)

        fiscal_data = [
            [
                "Rendimento Bruto (Receita)",
                total_income,
                "Total recebido dos apps/passageiros",
            ],
            ["(-) Despesa: Combustível", fuel_total, "Dutível conforme regulamento"],
            ["(-) Despesa: Manutenção", maint_total, "Dutível conforme regulamento"],
            [
                "VALOR LÍQUIDO TRIBUTÁVEL",
                total_income - (fuel_total + maint_total),
                "Base sugerida para cálculo de imposto",
            ],
        ]

        for row, item in enumerate(fiscal_data, start=1):
            fmt = bold_money_fmt if row == 4 else money_fmt
            ws_fiscal.write(row, 0, item[0], border_fmt)
            ws_fiscal.write(row, 1, item[1], fmt)
            ws_fiscal.write(row, 2, item[2], border_fmt)

        workbook.close()
        output.seek(0)

        filename = f"Relatorio_Fiscal_{month}_{year}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class FiscalPreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_pro:
            return Response(
                {"error": "Exclusivo PRO"}, status=status.HTTP_403_FORBIDDEN
            )

        month = request.query_params.get("month")
        year = request.query_params.get("year")

        records = DailyRecord.objects.filter(
            user=user, date__month=month, date__year=year, is_active=False
        )
        total_income = float(
            records.aggregate(Sum("total_income"))["total_income__sum"] or 0
        )

        transactions = Transaction.objects.filter(
            record__user=user, record__date__month=month, record__date__year=year
        )

        # CORREÇÃO AQUI: Filtrando pela Flag
        fuel_total = float(
            transactions.filter(category__is_fuel=True).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )
        maint_total = float(
            transactions.filter(category__is_maintenance=True).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        return Response(
            {
                "month": month,
                "year": year,
                "total_income": total_income,
                "fuel_total": fuel_total,
                "maint_total": maint_total,
                "tax_base": total_income - (fuel_total + maint_total),
                "currency": "BRL",
            }
        )


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

            op_cost = ops_dict.get(month_date, 0) or 0
            maintenance_cost = maint_dict.get(month_date, 0) or 0

            total_income = item["total_income"] or 0
            total_km = item["total_km"] or 0

            total_cost_real = op_cost + maintenance_cost
            profit = total_income - total_cost_real

            income_per_km = (total_income / total_km) if total_km > 0 else 0
            cost_per_km = (total_cost_real / total_km) if total_km > 0 else 0
            profit_per_km = (profit / total_km) if total_km > 0 else 0

            data.append(
                {
                    "month": month_date.strftime("%Y-%m"),
                    "display_month": month_date.strftime("%B/%Y"),
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
