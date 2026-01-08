from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Category, Transaction


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        Category.objects.create(
            user=instance, name="Abastecimento", type="COST", color="#ef4444", is_fuel=True,
        )
        Category.objects.create(
            user=instance, name="Manutenção", type="COST", color="#f97316", is_maintenance=True,
        )
        Category.objects.create(
            user=instance, name="Alimentação", type="COST", color="#eab308"
        )
        Category.objects.create(
            user=instance, name="Outros", type="COST", color="#64748b"
        )


@receiver(post_save, sender=Transaction)
@receiver(post_delete, sender=Transaction)
def update_daily_record_totals(sender, instance, **kwargs):
    """
    Sempre que uma transação é salva ou deletada, recalcula
    os totais de Receita e Custo do Registro Diário (DailyRecord) vinculado.
    """
    record = instance.record

    totals = record.transactions.values("type").annotate(total=Sum("amount"))

    total_income = 0
    total_cost = 0

    for t in totals:
        if t["type"] == "INCOME":
            total_income = t["total"] or 0
        elif t["type"] == "COST":
            total_cost = t["total"] or 0

    record.total_income = total_income
    record.total_cost = total_cost
    record.save(update_fields=["total_income", "total_cost"])
