from django.db import models
from apps.user.models import Usuario, Roles
from apps.clases.models import Clases
from apps.cursos.models import Cursos

# Create your models here.


class Docente(models.Model):

    telefono = models.IntegerField('telefono')
    direccion = models.CharField('direccion', max_length=50)
    usuario = models.ForeignKey(Usuario,on_delete=models.CASCADE, related_name="docente")

    rol = models.ForeignKey(Roles,on_delete=models.CASCADE, related_name="rol")
    clase = models.ForeignKey(Clases,on_delete=models.CASCADE, related_name="clase")
    curso = models.ForeignKey(Cursos,on_delete=models.CASCADE, related_name="curso")

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} {self.curso} - {self.curso}"