from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    is_pro_legacy = models.BooleanField("PRO Manual (Legado)", default=False)

    pro_expiry_date = models.DateField(
        "Expira em",
        null=True,
        blank=True,
        help_text="O usuário é PRO até esta data (inclusive).",
    )
    daily_goal = models.DecimalField(
        "Meta Diária", max_digits=10, decimal_places=2, default=0, blank=True, null=True
    )

    def __str__(self):
        return self.username

    @property
    def is_pro(self):
        if self.is_superuser:
            return True

        if self.pro_expiry_date:
            return self.pro_expiry_date >= timezone.now().date()

        return self.is_pro_legacy

    @property
    def plan_name(self):
        return "PRO" if self.is_pro else "Grátis"
