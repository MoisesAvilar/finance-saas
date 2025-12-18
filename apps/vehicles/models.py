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

    def __str__(self):
        return f"{self.model_name} ({self.plate})"

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
