import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
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


class ExportReportView(APIView):
    """
    Gera o Excel (.xlsx) detalhado (funcionalidade PRO).
    Retorna o arquivo binário diretamente.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_pro:
            return Response(
                {"detail": "Funcionalidade exclusiva para usuários PRO."},
                status=status.HTTP_403_FORBIDDEN,
            )

        WEEKDAYS = {
            0: "Segunda-feira",
            1: "Terça-feira",
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo",
        }

        records = (
            DailyRecord.objects.filter(user=request.user, is_active=False)
            .order_by("-date")
            .prefetch_related("transactions", "vehicle")
        )

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Relatório Financeiro"

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(
            start_color="1e293b", end_color="1e293b", fill_type="solid"
        )
        center_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        headers = [
            "Data",
            "Dia Semana",
            "Veículo",
            "Placa",
            "KM Inicial",
            "KM Final",
            "Rodagem (km)",
            "Receita",
            "Combustível",
            "Manutenção",
            "Outros",
            "Custo Total",
            "Lucro Líquido",
            "R$/km",
        ]
        sheet.append(headers)

        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        row_num = 2
        for record in records:
            fuel_cost = sum(
                t.amount for t in record.transactions.all() if t.category.is_fuel
            )
            maint_cost = sum(
                t.amount for t in record.transactions.all() if t.category.is_maintenance
            )
            other_cost = record.total_cost - (fuel_cost + maint_cost)

            income_per_km = (
                (record.profit / record.km_driven) if record.km_driven else 0
            )

            row = [
                record.date,
                WEEKDAYS[record.date.weekday()],
                record.vehicle.model_name,
                record.vehicle.plate,
                record.start_km,
                record.end_km,
                record.km_driven,
                float(record.total_income),
                float(fuel_cost),
                float(maint_cost),
                float(other_cost),
                float(record.total_cost),
                float(record.profit),
                float(round(income_per_km, 2)),
            ]
            sheet.append(row)

            date_cell = sheet.cell(row=row_num, column=1)
            date_cell.number_format = "DD/MM/YYYY"

            currency_format = "R$ #,##0.00;[Red]-R$ #,##0.00"
            for col_idx in range(8, 15):
                cell = sheet.cell(row=row_num, column=col_idx)
                cell.number_format = currency_format

            profit_cell = sheet.cell(row=row_num, column=13)
            if record.profit < 0:
                profit_cell.font = Font(color="DC2626", bold=True)
            elif record.profit > 0:
                profit_cell.font = Font(color="16A34A", bold=True)

            for col in range(1, 15):
                cell = sheet.cell(row=row_num, column=col)
                cell.border = thin_border
                if col != 3:
                    cell.alignment = center_align

            row_num += 1

        column_widths = [12, 18, 20, 12, 10, 10, 10, 15, 15, 15, 12, 15, 18, 10]
        for i, width in enumerate(column_widths, 1):
            sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            'attachment; filename="Relatorio_Financeiro_PRO.xlsx"'
        )
        workbook.save(response)

        return response
