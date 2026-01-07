from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CategoryViewSet,
    DailyRecordViewSet,
    TransactionViewSet,
    MaintenanceViewSet,
    OnboardUserView,
    GetLastKmView,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"records", DailyRecordViewSet, basename="dailyrecord")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"maintenances", MaintenanceViewSet, basename="maintenance")

urlpatterns = [
    path("", include(router.urls)),
    path("onboard/", OnboardUserView.as_view(), name="api_onboard"),
    path("get-km/<int:vehicle_id>/", GetLastKmView.as_view(), name="api_get_km"),
]
