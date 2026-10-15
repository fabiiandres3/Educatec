from django.contrib import admin
from .models import Usuario, Roles

# Register your models here.

admin.site.register(Roles)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'documento',
        "first_name",
        "last_name",
        "fecha_nacimiento",
        "edad",
        "email",
        "rol",
    )

    fields = (
        'documento',
        "first_name",
        "last_name",
        "fecha_nacimiento",
        "email",
        "rol",
    )
