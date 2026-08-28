from django.db import models
from django.core.exceptions import ValidationError
from apps.user.models import Usuario
from apps.cursos.models import Cursos
from apps.clases.models import Clases


class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="docente")

    telefono = models.IntegerField('telefono', blank=True, null=True)
    direccion = models.CharField(max_length=100)
    curso = models.ForeignKey(Cursos, on_delete=models.SET_NULL, null=True, blank=True)
    clase = models.ForeignKey(Clases, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name}"


MAX_CURSOS_POR_DOCENTE = 3


class AsignacionDocente(models.Model):
    docente = models.ForeignKey(
        Docente,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )
    clase = models.ForeignKey(Clases, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("docente", "clase")
        verbose_name = "Asignación de docente"
        verbose_name_plural = "Asignaciones de docentes"

    def clean(self):

        if not self.docente_id:
            return

        if not self.pk:
            total = AsignacionDocente.objects.filter(docente=self.docente).count()
            if total >= MAX_CURSOS_POR_DOCENTE:
                raise ValidationError(
                    f"El docente {self.docente} ya tiene el máximo de "
                    f"{MAX_CURSOS_POR_DOCENTE} cursos/materias asignadas."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.docente} - {self.clase}"