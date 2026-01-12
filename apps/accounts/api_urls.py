from django.urls import path
from .api_views import (
    UserProfileView,
    RegisterView,
    ChangePasswordView,
    DeleteAccountView,
    GoogleLogin,
)

urlpatterns = [
    path("me/", UserProfileView.as_view(), name="user_profile"),
    path("register/", RegisterView.as_view(), name="user_register"),
    path("password/change/", ChangePasswordView.as_view(), name="user_password_change"),
    path("delete/", DeleteAccountView.as_view(), name="user_delete_account"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
]
