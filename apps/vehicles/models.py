from django.db import models
from django.conf import settings
from common.models import TimeStampedModel


class Vehicle(TimeStampedModel):
    FUEL_CHOICES = (
        ("GASOLINA", "Gasolina"),
        ("ETANOL", "Etanol"),
        ("DIESEL", "Diesel"),
        ("GNV", "GNV"),
        ("ELETRICO", "Elétrico"),
        ("FLEX", "Flex"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles"
    )
    model_name = models.CharField("Modelo", max_length=100)
    plate = models.CharField("Placa", max_length=20, blank=True)
    fuel_type = models.CharField(
        "Combustível", max_length=10, choices=FUEL_CHOICES, default="FLEX"
    )
    initial_km = models.PositiveIntegerField("Km Inicial no App")
    is_active = models.BooleanField("Ativo?", default=True)

    @property
    def current_odometer(self):
        last_shift_km = self.dailyrecord_set.aggregate(m=Max("end_km"))["m"] or 0
        current_shift_km = self.dailyrecord_set.aggregate(m=Max("start_km"))["m"] or 0
        from operations.models import Transaction

        last_trans_km = (
            Transaction.objects.filter(record__vehicle=self).aggregate(
                m=Max("actual_km")
            )["m"]
            or 0
        )

        return max(self.initial_km, last_shift_km, current_shift_km, last_trans_km)

    @property
    def fuel_average(self):
        from operations.models import Transaction

        fills = Transaction.objects.filter(
            record__vehicle=self,
            category__is_fuel=True,
            actual_km__isnull=False,
            liters__isnull=False,
        ).order_by("-created_at")[:2]

        if len(fills) < 2:
            return None

        last_fill = fills[0]
        prev_fill = fills[1]

        km_driven = last_fill.actual_km - prev_fill.actual_km
        if km_driven <= 0 or last_fill.liters <= 0:
            return 0

        return km_driven / float(last_fill.liters)

    @property
    def maintenance_status(self):
        from operations.models import Transaction

        last_maint = (
            Transaction.objects.filter(record__vehicle=self, next_due_km__isnull=False)
            .order_by("-created_at")
            .first()
        )

        if not last_maint:
            return None

        current = self.current_odometer
        due = last_maint.next_due_km
        remaining = due - current

        if remaining <= 0:
            return {
                "status": "danger",
                "msg": f"Venceu há {abs(remaining)} km!",
                "percent": 100,
            }
        elif remaining < 500:
            return {"status": "warning", "msg": f"Faltam {remaining} km", "percent": 90}
        else:
            return {
                "status": "success",
                "msg": f"Tudo ok ({remaining} km)",
                "percent": 50,
            }

    def __str__(self):
        return f"{self.model_name} ({self.plate})"

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
