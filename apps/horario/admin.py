from django.contrib import admin
from .models import Horario, Periodo


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "anio",
        "fecha_inicio",
        "fecha_fin",
        "activo",
    )


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "periodo",
        "curso",
        "docente",
        "clase",
        "dia",
        "jornada",
        "hora_inicio",
        "hora_fin",
    )

    list_filter = (
        "periodo",
        "curso",
        "dia",
        "jornada",
    )