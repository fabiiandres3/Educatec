from django.contrib import admin
from .models import Docente, AsignacionDocente

# Register your models here.

admin.site.register(Docente)

@admin.register(AsignacionDocente)
class AsignacionDocenteAdmin(admin.ModelAdmin):
    list_display = ("docente", "clase")
    list_filter = ("docente",)