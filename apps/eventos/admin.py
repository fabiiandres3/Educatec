from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):

    list_display = (
        "titulo",
        "tipo",
        "fecha",
        "hora",
        "publico",
        "publicado",
    )

    list_filter = (
        "tipo",
        "publico",
        "publicado",
        "fecha",
    )

    search_fields = (
        "titulo",
        "descripcion",
    )

    ordering = (
        "fecha",
        "hora",
    )