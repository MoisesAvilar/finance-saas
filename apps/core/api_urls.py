from django.urls import path
from .api_views import DashboardSummaryView, PricingInfoView

urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="api_dashboard"),
    path("pricing/", PricingInfoView.as_view(), name="api_pricing"),
]
