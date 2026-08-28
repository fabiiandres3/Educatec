from django import forms
from apps.docentes.models import Docente, AsignacionDocente


class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = [
            "telefono",
            "direccion",
            "curso",
            "clase"
        ]


class AsignacionDocenteForm(forms.ModelForm):
    class Meta:
        model = AsignacionDocente
        fields = ["clase"]