from django.db import models

from apps.user.models import Usuario
from apps.cursos.models import Cursos
from apps.clases.models import Clases


# =========================================================
# ALUMNO
# =========================================================

class Alumnos(models.Model):

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="alumno"
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    curso = models.ForeignKey(
        Cursos,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    clase = models.ForeignKey(
        Clases,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    fecha_nacimiento = models.DateField(
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    direccion = models.TextField(
        blank=True,
        null=True
    )

    fecha_ingreso = models.DateField(
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):

        return (
            f"{self.usuario.get_full_name()} "
            f"({self.codigo or 'Sin código'})"
        )


# =========================================================
# ACUDIENTE
# =========================================================

class Acudiente(models.Model):

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="acudiente"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    direccion = models.TextField(
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        nombre = self.usuario.get_full_name()

        return nombre or self.usuario.username


# =========================================================
# RELACIÓN ACUDIENTE - ALUMNO
# =========================================================

class AcudienteAlumno(models.Model):

    acudiente = models.ForeignKey(
        Acudiente,
        on_delete=models.CASCADE,
        related_name="relaciones_alumnos"
    )

    alumno = models.ForeignKey(
        Alumnos,
        on_delete=models.CASCADE,
        related_name="relaciones_acudientes"
    )

    parentesco = models.CharField(
        max_length=50,
        default="Acudiente"
    )

    es_principal = models.BooleanField(
        default=True
    )

    autorizado = models.BooleanField(
        default=True
    )

    fecha_vinculacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        verbose_name = "Relación acudiente-alumno"

        verbose_name_plural = "Relaciones acudiente-alumno"

        constraints = [

            models.UniqueConstraint(
                fields=["acudiente", "alumno"],
                name="unique_acudiente_alumno"
            )

        ]

    def __str__(self):

        return (
            f"{self.acudiente} → "
            f"{self.alumno}"
        )