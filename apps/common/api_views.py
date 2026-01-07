from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Banner
from .serializers import BannerSerializer


class BannerListView(generics.ListAPIView):
    serializer_class = BannerSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_pro:
            return Banner.objects.none()

        queryset = Banner.objects.filter(active=True)

        position = self.request.query_params.get("position")
        if position:
            queryset = queryset.filter(position=position)

        return queryset.order_by("?")


class BannerClickView(APIView):
    """
    Substitui a view 'click_banner' do monolito.
    O Frontend chama isso para contabilizar o clique antes de redirecionar.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)

        if banner.active:
            banner.clicks += 1
            banner.save()

        return Response({"link": banner.link}, status=status.HTTP_200_OK)
