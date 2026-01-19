from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class GoogleAuthAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        id_token_str = request.data.get("id_token")

        if not id_token_str:
            return Response(
                {"detail": "id_token é obrigatório"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            google_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                audience=[
                    settings.GOOGLE_CLIENT_ID_WEB,
                    settings.GOOGLE_CLIENT_ID_ANDROID,
                ],
            )
        except ValueError:
            return Response(
                {"detail": "Token Google inválido"}, status=status.HTTP_401_UNAUTHORIZED
            )

        email = google_info.get("email")
        first_name = google_info.get("given_name", "")
        last_name = google_info.get("family_name", "")

        if not email:
            return Response(
                {"detail": "Email não encontrado no token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )
