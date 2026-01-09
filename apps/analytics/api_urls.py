from django.urls import path
from .api_views import MonthlyReportView, ExportReportView, FiscalPreviewView

urlpatterns = [
    path('export-report/', ExportReportView.as_view(), name='export-report'),
    path('fiscal-preview/', FiscalPreviewView.as_view(), name='fiscal-preview'),
    path("monthly/", MonthlyReportView.as_view(), name="api_monthly_report"),
    path("export/", ExportReportView.as_view(), name="api_export_report"),
]
