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
        "mostrar_usuario",
        "mostrar_nombre",
        "mostrar_apellido",
        "mostrar_correo",
        "mostrar_rol",
        "curso",
        "activo",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "usuario__email",
        "usuario__rol__nombre",
    )

    list_filter = (
        "activo",
        "curso",
        "usuario__rol",
    )

    @admin.display(description="Usuario")
    def mostrar_usuario(self, obj):

        return obj.usuario.username

    @admin.display(description="Nombre")
    def mostrar_nombre(self, obj):

        return obj.usuario.first_name or "—"

    @admin.display(description="Apellido")
    def mostrar_apellido(self, obj):

        return obj.usuario.last_name or "—"

    @admin.display(description="Correo")
    def mostrar_correo(self, obj):

        return obj.usuario.email or "—"

    @admin.display(description="Rol")
    def mostrar_rol(self, obj):

        if obj.usuario.rol:
            return obj.usuario.rol.nombre

        return "Sin rol"

