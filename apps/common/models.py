from django.db import models


class TimeStampedModel(models.Model):
    """
    Classe abstrata que adiciona campos created_at e updated_at
    a qualquer modelo que herdar dela.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True
