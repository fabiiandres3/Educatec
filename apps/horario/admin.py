from django.contrib import admin

from .models import Periodo


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