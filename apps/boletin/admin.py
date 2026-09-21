from django.contrib import admin

from .models import ContenidoPedagogico, ObservacionBoletin


@admin.register(ContenidoPedagogico)
class ContenidoPedagogicoAdmin(admin.ModelAdmin):
    list_display = ("asignacion", "periodo", "actualizado_en")
    list_filter = ("periodo",)


@admin.register(ObservacionBoletin)
class ObservacionBoletinAdmin(admin.ModelAdmin):
    list_display = ("alumno", "contenido", "actualizado_en")
    list_filter = ("contenido__periodo",)
