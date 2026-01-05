from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    current_odometer = serializers.ReadOnlyField()
    fuel_average = serializers.ReadOnlyField()
    maintenance_status = serializers.ReadOnlyField()
    formatted_created_at = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "model_name",
            "plate",
            "fuel_type",
            "initial_km",
            "is_active",
            "current_odometer",
            "fuel_average",
            "maintenance_status",
            "created_at",
            "formatted_created_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_formatted_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")

    def validate_initial_km(self, value):
        if value < 0:
            raise serializers.ValidationError("A quilometragem não pode ser negativa.")
        return value

    def validate_plate(self, value):
        return value.upper().replace("-", "").strip() if value else value
