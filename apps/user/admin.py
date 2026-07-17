from django.contrib import admin
from .models import Usuario, Roles

# Register your models here.

admin.site.register(Roles)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        "first_name",
        "last_name",
        "email",
        "rol",
    )

    fields = (
        'username',
        "first_name",
        "last_name",
        "email",
        "rol",
    )