from rest_framework import serializers
from django.utils import timezone
from .models import Category, DailyRecord, Transaction, Maintenance
from vehicles.models import Vehicle


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type", "color", "is_fuel", "is_maintenance", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "O nome deve ter pelo menos 2 caracteres."
            )
        return value


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    category_color = serializers.ReadOnlyField(source="category.color")
    category_is_fuel = serializers.ReadOnlyField(source="category.is_fuel")
    category_is_maintenance = serializers.ReadOnlyField(source="category.is_maintenance")
    formatted_created_at = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "record",
            "category",
            "category_name",
            "category_color",
            "category_is_fuel",
            "category_is_maintenance",
            "description",
            "amount",
            "type",
            "actual_km",
            "liters",
            "is_full_tank",
            "next_due_km",
            "created_at",
            "updated_at",
            "formatted_created_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_formatted_created_at(self, obj):
        return obj.created_at.strftime("%H:%M")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser maior que zero.")
        return value
    
    def to_representation(self, instance):
        """
        Se o next_due_km estiver vazio na Transação, tenta buscar
        no registro de Manutenção vinculado (Espelho).
        """
        data = super().to_representation(instance)
        
        if not data.get('next_due_km'):
            if hasattr(instance, 'maintenance_mirror'):
                mirror = instance.maintenance_mirror.first()
                if mirror and mirror.next_due_km:
                    data['next_due_km'] = mirror.next_due_km
        
        return data


class DailyRecordSerializer(serializers.ModelSerializer):
    vehicle_model = serializers.ReadOnlyField(source="vehicle.model_name")
    vehicle_plate = serializers.ReadOnlyField(source="vehicle.plate")
    formatted_date = serializers.SerializerMethodField()

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
            "created_at",
            "updated_at",
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
        read_only_fields = ["user", "total_income", "total_cost"]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")

    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("A data não pode ser no futuro.")
        return value

    def validate_start_km(self, value):
        if value < 0:
            raise serializers.ValidationError("A quilometragem não pode ser negativa.")
        return value

    def validate(self, data):
        """
        Validação cruzada (Start KM vs End KM)
        """
        if self.instance and "end_km" in data:
            start = self.instance.start_km
            end = data["end_km"]

            if end is not None:
                if end < start:
                    raise serializers.ValidationError(
                        {"end_km": "O KM final não pode ser menor que o inicial."}
                    )

                if (end - start) > 2000:
                    raise serializers.ValidationError(
                        {
                            "end_km": "A distância percorrida parece muito alta (>2000km). Verifique se digitou corretamente."
                        }
                    )

        return data
    
    def validate_vehicle(self, value):
        """
        IMPEDE O USO DE VEÍCULOS 'CONGELADOS' NO PLANO FREE.
        Mesmo que o veículo esteja active=True no banco, se o usuário for Free,
        ele só pode usar o veículo mais recente (ou o único permitido).
        """
        request = self.context.get('request')
        user = request.user

        if getattr(user, 'is_pro', False):
            return value

        if value.user != user:
            raise serializers.ValidationError("Veículo inválido.")

        allowed_vehicle = Vehicle.objects.filter(
            user=user, 
            is_active=True
        ).order_by('-id').first()

        if allowed_vehicle and value.id != allowed_vehicle.id:
            raise serializers.ValidationError(
                "Acesso Negado. Este veículo está congelado no seu Plano Grátis. "
                "Utilize seu veículo principal ou faça Upgrade para liberar a frota."
            )

        return value


class MaintenanceSerializer(serializers.ModelSerializer):
    vehicle_model = serializers.ReadOnlyField(source="vehicle.model_name")
    formatted_date = serializers.SerializerMethodField()
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    maintenance_status = serializers.SerializerMethodField()

    class Meta:
        model = Maintenance
        fields = [
            "id",
            "vehicle",
            "vehicle_model",
            "date",
            "formatted_date",
            "type",
            "type_display",
            "description",
            "cost",
            "odometer",
            "transaction",
            "next_due_km",
            "maintenance_status",
        ]
        read_only_fields = ["user", "transaction"]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")

    def get_maintenance_status(self, obj):
        if not obj.next_due_km:
            return None

        current_km = obj.vehicle.current_odometer
        remaining = obj.next_due_km - current_km

        if remaining < 0:
            return {
                "status": "danger",
                "label": "VENCIDA",
                "msg": f"Passou {abs(remaining)} km",
                "class": "bg-red-100 text-red-700 border-red-200",
            }
        elif remaining < 1000:
            return {
                "status": "warning",
                "label": "ATENÇÃO",
                "msg": f"Faltam {remaining} km",
                "class": "bg-amber-100 text-amber-700 border-amber-200",
            }
        else:
            return {
                "status": "ok",
                "label": "EM DIA",
                "msg": f"Faltam {remaining} km",
                "class": "bg-green-100 text-green-700 border-green-200",
            }


class DailyRecordDetailSerializer(DailyRecordSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta(DailyRecordSerializer.Meta):
        fields = DailyRecordSerializer.Meta.fields + ["transactions"]
