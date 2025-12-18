from django.urls import path
from .views import MonthlyPerformanceView

urlpatterns = [
    path('', MonthlyPerformanceView.as_view(), name='analytics_monthly'),
]
