from django.db import models
from django.conf import settings
from common.models import TimeStampedModel
from vehicles.models import Vehicle


class DailyRecord(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    date = models.DateField("Data do Registro")
    start_km = models.PositiveIntegerField("Km Inicial")
    end_km = models.PositiveIntegerField("Km Final", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_income = models.DecimalField(
        "Ganhos Totais", max_digits=10, decimal_places=2, default=0
    )
    total_cost = models.DecimalField(
        "Custos Totais", max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = "Registro Diário"
        verbose_name_plural = "Registros Diários"
        unique_together = ["user", "date"]
        ordering = ["-date"]

    def __str__(self):
        status = "Aberto" if self.is_active else "Fechado"
        return f"{self.date} - {self.vehicle} ({status})"

    @property
    def km_driven(self):
        if self.end_km is None:
            return 0
        return max(0, self.end_km - self.start_km)

    @property
    def profit(self):
        return self.total_income - self.total_cost

    @property
    def cost_per_km(self):
        km = self.km_driven
        if km > 0:
            return self.total_cost / km
        return 0

    @property
    def income_per_km(self):
        km = self.km_driven
        if km > 0:
            return self.total_income / km
        return 0


class Maintenance(TimeStampedModel):
    TYPE_CHOICES = (
        ("OIL", "Troca de Óleo"),
        ("TIRES", "Pneus"),
        ("MECHANIC", "Mecânica Geral"),
        ("ELECTRICAL", "Elétrica"),
        ("DOCUMENTATION", "Documentação/IPVA"),
        ("CLEANING", "Estética/Limpeza Pesada"),
        ("OTHER", "Outros"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField("Data")
    odometer = models.PositiveIntegerField("KM no momento")
    cost = models.DecimalField("Valor (R$)", max_digits=10, decimal_places=2)
    type = models.CharField("Tipo", max_length=20, choices=TYPE_CHOICES)
    description = models.CharField("Descrição/Oficina", max_length=200, blank=True)

    class Meta:
        verbose_name = "Manutenção"
        verbose_name_plural = "Manutenções"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_type_display()} - {self.vehicle}"


class Category(TimeStampedModel):
    TYPE_CHOICES = (
        ("INCOME", "Receita"),
        ("COST", "Despesa"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField("Nome", max_length=50)
    type = models.CharField("Tipo", max_length=10, choices=TYPE_CHOICES)
    color = models.CharField(
        "Cor (Hex)", max_length=7, default="#64748b"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(TimeStampedModel):
    TYPE_CHOICES = (
        ("INCOME", "Receita"),
        ("COST", "Despesa"),
    )

    record = models.ForeignKey(
        DailyRecord, on_delete=models.CASCADE, related_name="transactions"
    )
    type = models.CharField("Tipo", max_length=10, choices=TYPE_CHOICES)

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name="Categoria"
    )

    amount = models.DecimalField("Valor (R$)", max_digits=10, decimal_places=2)
    description = models.CharField("Descrição", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.category.name} - R$ {self.amount}"
