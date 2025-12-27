from django.urls import path
from .views import PricingView

urlpatterns = [
    path("planos/", PricingView.as_view(), name="pricing"),
]
