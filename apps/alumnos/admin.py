from django.contrib import admin

from .models import (
    Alumnos,
    Acudiente,
    AcudienteAlumno,
)


# =========================================================
# RELACIÓN ACUDIENTE - ALUMNO
# =========================================================

class AcudienteAlumnoInline(admin.TabularInline):

    model = AcudienteAlumno

    extra = 1

    fields = [
        "alumno",
        "parentesco",
        "es_principal",
        "autorizado",
    ]


# =========================================================
# ACUDIENTE
# =========================================================

@admin.register(Acudiente)
class AcudienteAdmin(admin.ModelAdmin):

    list_display = (
        "nombre_acudiente",
        "email",
        "telefono",
        "activo",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "usuario__email",
    )

    list_filter = (
        "activo",
    )

    inlines = [
        AcudienteAlumnoInline
    ]

    @admin.display(description="Acudiente")
    def nombre_acudiente(self, obj):

        return (
            obj.usuario.get_full_name()
            or obj.usuario.username
        )

    @admin.display(description="Correo")
    def email(self, obj):

        return obj.usuario.email


# =========================================================
# ALUMNOS
# =========================================================

@admin.register(Alumnos)
class AlumnosAdmin(admin.ModelAdmin):

    list_display = (
        "usuario",
        "codigo",
        "curso",
        "clase",
        "activo",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "usuario__email",
        "codigo",
    )

    list_filter = (
        "activo",
        "curso",
    )