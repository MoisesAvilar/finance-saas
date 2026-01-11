from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True


class Banner(TimeStampedModel):
    POSITIONS = (("DASHBOARD_TOP", "Topo do Dashboard"),)

    title = models.CharField("Título Interno", max_length=100)
    image = models.ImageField("Imagem do Banner", upload_to="banners/")
    link = models.URLField("Link de Destino (Afiliado)")
    position = models.CharField(
        max_length=20, choices=POSITIONS, default="DASHBOARD_TOP"
    )
    active = models.BooleanField("Ativo?", default=True)
    clicks = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = "Banner de Publicidade"
        verbose_name_plural = "Banners de Publicidade"

    def __str__(self):
        return self.title
