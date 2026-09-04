from django.contrib import admin

from .models import Evento


class EventoAdmin(admin.ModelAdmin):

    list_display = (
        "titulo",
        "tipo",
        "fecha",
        "hora",
        "lugar",
        "activo",
    )

    list_filter = (
        "tipo",
        "fecha",
        "activo",
    )