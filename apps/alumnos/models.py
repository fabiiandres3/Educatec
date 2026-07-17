from django.db import models
from apps.user.models import Usuario

class Alumnos(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="alumno"
    )

    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    nombre_acudiente = models.CharField(max_length=150, blank=True, null=True)
    telefono_acudiente = models.CharField(max_length=20, blank=True, null=True)
    parentesco_acudiente = models.CharField(max_length=50, blank=True, null=True)

    fecha_ingreso = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.codigo or 'Sin código'})"