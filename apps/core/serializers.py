from rest_framework import serializers
from operations.models import DailyRecord, Category


class DashboardCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type", "color", "is_fuel", "is_maintenance"]


class DashboardRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRecord
        fields = ["id", "date", "total_income", "total_cost", "km_driven", "is_active"]


class ActiveShiftSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()

    class Meta:
        model = DailyRecord
        fields = ["id", "start_km", "start_time", "vehicle"]

    def get_start_time(self, obj):
        return obj.created_at.strftime("%H:%M")
