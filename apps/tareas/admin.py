from django.contrib import admin
from .models import Calificacion, RespuestaAlumno, Tareas

# Register your models here.

admin.site.register(Tareas)
admin.site.register(Calificacion)

admin.site.register(RespuestaAlumno)