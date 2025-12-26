from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Category


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        Category.objects.create(
            user=instance, name="App (Uber/99)", type="INCOME", color="#10b981"
        )
        Category.objects.create(
            user=instance, name="Particular", type="INCOME", color="#059669"
        )

        Category.objects.create(
            user=instance,
            name="Abastecimento",
            type="COST",
            color="#ef4444",
            is_fuel=True,
        )
        Category.objects.create(
            user=instance,
            name="Manutenção",
            type="COST",
            color="#f97316",
            is_maintenance=True,
        )

        Category.objects.create(
            user=instance, name="Alimentação", type="COST", color="#eab308"
        )
        Category.objects.create(
            user=instance, name="Outros", type="COST", color="#64748b"
        )
