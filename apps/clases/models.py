from django.db import models
from apps.cursos.models import Cursos


class Clases(models.Model):

    titulo = models.CharField(
        "Título",
        max_length=100
    )

    cursos = models.ManyToManyField(
        Cursos,
        blank=True,
        related_name="clases"
    )

    class Meta:
        verbose_name = "Clase"
        verbose_name_plural = "Clases"

    def __str__(self):
        return self.titulo
