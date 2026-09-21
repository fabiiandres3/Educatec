from django.core.exceptions import ValidationError
from django.db import models
from apps.cursos.models import Cursos
from apps.clases.models import Clases
from apps.user.models import Usuario


MAX_MATERIAS_POR_DOCENTE = 3
MAX_CURSOS_POR_DOCENTE = 999

class Docente(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="docente"
    )

    telefono = models.IntegerField(
        null=True,
        blank=True
    )

    direccion = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username


class AsignacionDocente(models.Model):
    docente = models.ForeignKey(
        Docente,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )

    curso = models.ForeignKey(
        Cursos,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="asignaciones_docentes"
    )

    clase = models.ForeignKey(
        Clases,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="asignaciones_docentes"
    )

    class Meta:
        verbose_name = "Asignación de docente"
        verbose_name_plural = "Asignaciones de docentes"

    def __str__(self):
        if self.clase and self.curso:
            return f"{self.docente} - {self.clase} ({self.curso})"
        if self.curso:
            return f"{self.docente} - {self.curso}"
        return str(self.docente)