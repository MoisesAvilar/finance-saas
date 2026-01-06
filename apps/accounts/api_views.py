from rest_framework import generics, permissions
from .serializers import UserProfileSerializer, RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer