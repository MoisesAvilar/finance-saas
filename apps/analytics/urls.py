from django.urls import path
from .views import MonthlyPerformanceView, export_reports_excel

urlpatterns = [
    path("", MonthlyPerformanceView.as_view(), name="analytics_monthly"),
    path("exportar/", export_reports_excel, name="analytics_export"),
]
