from django.db import models
from apps.cursos.models import Cursos

# Create your models here.
class Clases(models.Model):
    titulo = models.CharField('Titulo',max_length=100)
    curso = models.ForeignKey(Cursos, on_delete=models.SET_NULL, blank=True, null=True)
    

    class Meta:
        verbose_name = 'clase'
        verbose_name_plural = 'clases'

    def __str__(self):
        return str(self.titulo)

