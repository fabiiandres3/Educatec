from django import forms
from .models import Alumnos


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumnos
        exclude = ["usuario"]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "fecha_ingreso": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Código del alumno"
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono"
            }),
            "direccion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Dirección"
            }),
            "nombre_acudiente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del acudiente"
            }),
            "telefono_acudiente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono del acudiente"
            }),
            "parentesco_acudiente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Parentesco"
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }