from django.db import models
from apps.cursos.models import Cursos


class Clases(models.Model):

    titulo = models.CharField(
        "Título",
        max_length=100
    )

    curso = models.ForeignKey(
        Cursos,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="clases"
    )

    class Meta:
        verbose_name = "Clase"
        verbose_name_plural = "Clases"

    def __str__(self):
        return self.titulo