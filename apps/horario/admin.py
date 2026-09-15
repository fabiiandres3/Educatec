from django.contrib import admin

from .models import Periodo, Horario


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "anio",
        "fecha_inicio",
        "fecha_fin",
        "activo",
    )

    list_filter = (
        "anio",
        "numero",
        "activo",
    )

    search_fields = (
        "anio",
    )

    ordering = (
        "-anio",
        "numero",
    )



@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "periodo",
        "docente",
        "curso",
        "clase",
        "dia",
        "jornada",
        "hora_inicio",
        "hora_fin",
    )

    list_filter = (
        "periodo",
        "docente",
        "curso",
        "jornada",
        "dia",
    )

    search_fields = (
        "docente__usuario__first_name",
        "docente__usuario__last_name",
        "curso__nombre",
        "clase__titulo",
    )

    ordering = (
        "periodo",
        "dia",
        "hora_inicio",
    )