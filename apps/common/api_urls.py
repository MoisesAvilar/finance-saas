from django.urls import path
from .api_views import BannerListView

urlpatterns = [
    path("banners/", BannerListView.as_view(), name="api_banners"),
]
