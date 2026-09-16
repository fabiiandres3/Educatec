from django.db import models
from apps.cursos.models import Cursos
from apps.user.models import Usuario


MAX_CURSOS_POR_DOCENTE = 3

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

    def __str__(self):
        return f"{self.docente} - {self.curso}"