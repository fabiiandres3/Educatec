from django import forms
from django.utils import timezone

from apps.user.models import Usuario


class CuentaPerfilForm(forms.ModelForm):
    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if Usuario.objects.filter(documento__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este documento ya está asociado con otra cuenta.")
        return username

    class Meta:
        model = Usuario
        fields = (
            "username", "first_name", "last_name", "fecha_nacimiento",
            "email", "telefono", "direccion",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "fecha_nacimiento": forms.DateInput(format="%Y-%m-%d", attrs={
                "type": "date",
                "autocomplete": "bday",
            }),
            "username": forms.TextInput(attrs={"autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "telefono": forms.TextInput(attrs={"autocomplete": "tel"}),
            "direccion": forms.TextInput(attrs={"autocomplete": "street-address"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "account-input"})
        self.fields["first_name"].label = "Nombres"
        self.fields["last_name"].label = "Apellidos"
        self.fields["fecha_nacimiento"].label = "Fecha de nacimiento"
        self.fields["username"].label = "Documento de identidad"
        self.fields["email"].label = "Correo electrÃ³nico"
        self.fields["telefono"].label = "TelÃ©fono"
        self.fields["direccion"].label = "DirecciÃ³n"

    def clean_fecha_nacimiento(self):
        if self.add_prefix("fecha_nacimiento") not in self.data:
            fecha = self.initial.get("fecha_nacimiento") or self.instance.fecha_nacimiento
        else:
            fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha >= timezone.localdate():
            raise forms.ValidationError("La fecha de nacimiento debe ser anterior a hoy.")
        return fecha
