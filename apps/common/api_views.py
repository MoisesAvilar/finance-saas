from rest_framework import generics, permissions
from .models import Banner
from .serializers import BannerSerializer


class BannerListView(generics.ListAPIView):
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_pro:
            return Banner.objects.none()

        return Banner.objects.filter(active=True).order_by("-created_at")
