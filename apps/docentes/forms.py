from django import forms
from apps.docentes.models import Docente, AsignacionDocente
from apps.user.models import Usuario


class EditarDocenteUsuarioForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
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
