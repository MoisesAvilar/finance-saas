from django.urls import path
from .api_views import UserProfileView, RegisterView

urlpatterns = [
    path("me/", UserProfileView.as_view(), name="user_profile"),
    path("register/", RegisterView.as_view(), name="user_register"),
]
