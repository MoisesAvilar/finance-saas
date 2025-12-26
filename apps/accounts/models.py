from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_pro = models.BooleanField(
        "Usuário PRO",
        default=False,
        help_text="Marque para liberar funcionalidades premium.",
    )


    def __str__(self):
        return self.username

    @property
    def plan_name(self):
        return "PRO" if self.is_pro else "Grátis"
