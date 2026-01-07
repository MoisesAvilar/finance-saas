from rest_framework import serializers
from .models import Vehicle
from operations.models import Maintenance


class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Maintenance
        fields = [
            "id",
            "date",
            "formatted_date",
            "odometer",
            "cost",
            "type",
            "type_display",
            "description",
        ]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")


class VehicleSerializer(serializers.ModelSerializer):
    odometer = serializers.ReadOnlyField(source="current_odometer")
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
            "odometer",
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

    def validate_model_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "O nome do modelo deve ser mais descritivo (mínimo 3 caracteres)."
            )
        return value
