from rest_framework import viewsets, permissions, serializers
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_pro:
            count = Vehicle.objects.filter(user=user).count()
            if count >= 1:
                raise serializers.ValidationError(
                    {
                        "detail": "Limite atingido. Usuários grátis só podem ter 1 veículo."
                    }
                )
        serializer.save(user=user)
