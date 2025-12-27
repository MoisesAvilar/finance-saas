from django.urls import path
from common.views import click_banner

urlpatterns = [
    path("click/<int:banner_id>/", click_banner, name="banner_click"),
]
