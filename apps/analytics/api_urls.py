from django.urls import path
from .api_views import MonthlyReportView, ExportReportView

urlpatterns = [
    path("monthly/", MonthlyReportView.as_view(), name="api_monthly_report"),
    path("export/", ExportReportView.as_view(), name="api_export_report"),
]
