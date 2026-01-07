from rest_framework import serializers
from django.apps import apps
from django.db.models import Sum
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

    stats = serializers.SerializerMethodField()
    consumption_history = serializers.SerializerMethodField()
    maintenance_history = serializers.SerializerMethodField()

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
            "stats",
            "consumption_history",
            "maintenance_history",
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

    def get_stats(self, obj):
        DailyRecord = apps.get_model('operations', 'DailyRecord')
        
        total_maint = Maintenance.objects.filter(vehicle=obj).aggregate(
            total=Sum('cost')
        )['total'] or 0

        records = DailyRecord.objects.filter(vehicle=obj, end_km__isnull=False)
        avg_km = 0
        if records.exists():
            total_km_driven = sum(r.km_driven for r in records)
            avg_km = total_km_driven / records.count()

        last_maint = Maintenance.objects.filter(
            vehicle=obj, 
            next_due_km__isnull=False
        ).order_by('-date').first()
        
        next_due = last_maint.next_due_km if last_maint else None
        last_date = last_maint.date.strftime("%d/%m/%Y") if last_maint else None

        return {
            "total_maintenance": total_maint,
            "avg_daily_km": round(avg_km, 1),
            "next_maintenance_km": next_due,
            "last_maintenance_date": last_date
        }

    def get_consumption_history(self, obj):
        Transaction = apps.get_model("operations", "Transaction")

        txs = Transaction.objects.filter(
            record__vehicle=obj,
            category__is_fuel=True,
            actual_km__isnull=False,
            liters__isnull=False,
        ).order_by("actual_km")

        history = []
        tx_list = list(txs)

        for i in range(1, len(tx_list)):
            prev = tx_list[i - 1]
            curr = tx_list[i]

            km_diff = curr.actual_km - prev.actual_km

            if km_diff > 0 and curr.liters > 0:
                avg = km_diff / float(curr.liters)

                if 4 < avg < 70:
                    history.append(
                        {
                            "km": f"{curr.actual_km}km",
                            "media": round(avg, 1),
                            "date": curr.record.date.strftime("%d/%m"),
                        }
                    )

        return history[-6:]

    def get_maintenance_history(self, obj):
        maints = Maintenance.objects.filter(vehicle=obj).order_by('-date')[:5]

        data = []
        for m in maints:
            data.append({
                "id": m.id,
                "description": m.description or m.get_type_display(),
                "date": m.date.strftime("%d/%m/%Y"),
                "km": m.odometer,
                "amount": m.cost
            })
        return data
