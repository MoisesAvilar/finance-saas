from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Aqui podemos adicionar campos futuros como 'is_premium', 'phone', etc.
    pass

    def __str__(self):
        return self.username
