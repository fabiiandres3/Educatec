from django.contrib import admin
from .models import Calificacion, RespuestaAlumno, Tareas

# Register your models here.

@admin.register(Tareas)
class TareasAdmin(admin.ModelAdmin):
    list_display = ("titulo", "curso", "clase", "periodo", "fecha_entrega", "activa")
    list_filter = ("periodo", "curso", "clase", "activa")


admin.site.register(Calificacion)

admin.site.register(RespuestaAlumno)
