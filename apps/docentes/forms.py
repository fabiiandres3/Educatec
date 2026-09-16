from django import forms
from apps.docentes.models import Docente, AsignacionDocente


class DocenteForm(forms.ModelForm):

    class Meta:
        model = Docente
        fields = [
            "usuario",
            "telefono",
            "direccion",
        ]

        widgets = {
            "usuario": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
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
        fields = ["curso"]

        widgets = {
            "curso": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
        }

        labels = {
            "curso": "Curso"
        }