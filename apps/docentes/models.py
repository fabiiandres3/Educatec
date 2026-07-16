from django.db import models
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
