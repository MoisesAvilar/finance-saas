from django.urls import path
from .api_views import DashboardSummaryView, PricingInfoView, ExportReportView

urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="api_dashboard"),
    path('dashboard/export/', ExportReportView.as_view(), name='dashboard-export'),
    path("pricing/", PricingInfoView.as_view(), name="api_pricing"),
]
