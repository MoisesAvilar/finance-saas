from rest_framework import serializers
from operations.models import DailyRecord, Category
from vehicles.models import Vehicle


class DashboardCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "color", "type", "is_fuel", "is_maintenance"]


class ActiveShiftSerializer(serializers.ModelSerializer):
    profit = serializers.ReadOnlyField()
    start_time = serializers.SerializerMethodField()

    class Meta:
        model = DailyRecord
        fields = [
            "id",
            "start_km",
            "start_time",
            "total_income",
            "total_cost",
            "profit",
            "is_active",
        ]

    def get_start_time(self, obj):
        return obj.created_at.strftime("%H:%M")


class DashboardRecordSerializer(serializers.ModelSerializer):
    vehicle_model = serializers.CharField(source="vehicle.model_name", read_only=True)
    formatted_date = serializers.SerializerMethodField()
    profit = serializers.ReadOnlyField()
    km_driven = serializers.ReadOnlyField()

    class Meta:
        model = DailyRecord
        fields = [
            "id",
            "date",
            "formatted_date",
            "vehicle_model",
            "total_income",
            "total_cost",
            "profit",
            "km_driven",
            "is_active",
        ]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m")
