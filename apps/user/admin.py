from django.contrib import admin
from django import forms
from .models import Usuario, Roles

# Register your models here.

admin.site.register(Roles)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    class FormularioUsuario(forms.ModelForm):
        def clean_username(self):
            username = self.cleaned_data["username"].strip()
            if Usuario.objects.filter(documento__iexact=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este documento ya está asociado con otra cuenta.")
            return username

        class Meta:
            model = Usuario
            fields = (
                "username",
                "first_name",
                "last_name",
                "fecha_nacimiento",
                "email",
                "rol",
            )
            labels = {"username": "Documento de identidad"}

    list_display = (
        'mostrar_documento',
        "first_name",
        "last_name",
        "fecha_nacimiento",
        "edad",
        "email",
        "rol",
    )

    fields = (
        'username',
        "first_name",
        "last_name",
        "fecha_nacimiento",
        "email",
        "rol",
    )
    form = FormularioUsuario

    @admin.display(description="Documento de identidad")
    def mostrar_documento(self, obj):
        return obj.username
