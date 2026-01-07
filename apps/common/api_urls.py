from django.urls import path
from .api_views import BannerListView, BannerClickView

urlpatterns = [
    path("banners/", BannerListView.as_view(), name="api_banners"),
    path("banners/<int:pk>/click/", BannerClickView.as_view(), name="api_banner_click"),
]