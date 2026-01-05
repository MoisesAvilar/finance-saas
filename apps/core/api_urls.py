from django.urls import path
from .api_views import DashboardSummaryView

urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="api_dashboard"),
]
