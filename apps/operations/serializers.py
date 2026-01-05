from rest_framework import serializers
from .models import Category, DailyRecord, Transaction, Maintenance
from vehicles.serializers import VehicleSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type", "color", "is_fuel", "is_maintenance"]
        read_only_fields = ["user"]


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    category_color = serializers.ReadOnlyField(source="category.color")
    formatted_created_at = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "record",
            "category",
            "category_name",
            "category_color",
            "description",
            "amount",
            "type",
            "actual_km",
            "liters",
            "next_due_km",
            "created_at",
            "formatted_created_at",
        ]

    def get_formatted_created_at(self, obj):
        return obj.created_at.strftime("%H:%M")


class DailyRecordSerializer(serializers.ModelSerializer):
    vehicle_model = serializers.ReadOnlyField(source="vehicle.model_name")
    vehicle_plate = serializers.ReadOnlyField(source="vehicle.plate")
    formatted_date = serializers.SerializerMethodField()

    # Campos calculados (properties do Model)
    total_income = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    profit = serializers.ReadOnlyField()
    km_driven = serializers.ReadOnlyField()
    income_per_km = serializers.ReadOnlyField()
    cost_per_km = serializers.ReadOnlyField()
    profit_per_km = serializers.ReadOnlyField()

    class Meta:
        model = DailyRecord
        fields = [
            "id",
            "vehicle",
            "vehicle_model",
            "vehicle_plate",
            "date",
            "formatted_date",
            "start_km",
            "end_km",
            "is_active",
            "total_income",
            "total_cost",
            "profit",
            "km_driven",
            "income_per_km",
            "cost_per_km",
            "profit_per_km",
        ]
        read_only_fields = ["user"]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")


class MaintenanceSerializer(serializers.ModelSerializer):
    vehicle_model = serializers.ReadOnlyField(source="vehicle.model_name")
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Maintenance
        fields = [
            "id",
            "vehicle",
            "vehicle_model",
            "date",
            "formatted_date",
            "type",
            "description",
            "cost",
            "odometer",
        ]
        read_only_fields = ["user"]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")
