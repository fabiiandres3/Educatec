from django import forms
from django.utils import timezone
from apps.docentes.models import Docente, AsignacionDocente
from apps.user.models import Usuario


class EditarDocenteUsuarioForm(forms.ModelForm):

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
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "autocomplete": "bday"}
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

        widgets = {
            "telefono": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Teléfono"
                }
            ),
            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección"
                }
            ),
        }


class AsignacionDocenteForm(forms.ModelForm):

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
