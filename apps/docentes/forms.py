from django import forms
from django.utils import timezone
from apps.docentes.models import Docente, AsignacionDocente
from apps.user.models import Usuario


class EditarDocenteUsuarioForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fecha_field = self.fields["fecha_nacimiento"]
        fecha_field.localize = False
        fecha_field.input_formats = ["%Y-%m-%d"]
        fecha_field.widget.format = "%Y-%m-%d"
        if self.instance and self.instance.pk and self.instance.fecha_nacimiento:
            self.initial["fecha_nacimiento"] = self.instance.fecha_nacimiento.isoformat()

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if Usuario.objects.filter(documento__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este documento ya está asociado con otra cuenta.")
        return username

    def clean_fecha_nacimiento(self):
        if self.add_prefix("fecha_nacimiento") not in self.data:
            fecha = self.instance.fecha_nacimiento
        else:
            fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha >= timezone.localdate():
            raise forms.ValidationError("La fecha de nacimiento debe ser anterior a hoy.")
        return fecha

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "fecha_nacimiento",
            "email",
        ]

        labels = {
            "username": "Documento de identidad",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "fecha_nacimiento": "Fecha de nacimiento",
            "email": "Correo electrónico",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),
            "fecha_nacimiento": forms.DateInput(format="%Y-%m-%d", attrs={"class": "form-control", "type": "date", "autocomplete": "bday"}
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }


class DocenteForm(forms.ModelForm):

    class Meta:
        model = Docente
        fields = [
            "telefono",
            "direccion",
        ]
        labels = {
            "telefono": "Teléfono",
            "direccion": "Dirección",
        }

        widgets = {
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "TelÃ©fono"
                }
            ),
            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "DirecciÃ³n"
                }
            ),
        }


class AsignacionDocenteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curso"].empty_label = "Seleccione un curso"
        self.fields["clase"].empty_label = "Seleccione una clase"

    class Meta:
        model = AsignacionDocente
        fields = ["curso", "clase"]
        widgets = {
            "curso": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
            "clase": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
        }

        labels = {
            "curso": "Curso",
            "clase": "Materia (Clase)"
        }
