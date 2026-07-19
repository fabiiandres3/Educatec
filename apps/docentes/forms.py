from django import forms
from apps.docentes.models import Docente


class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = [
            "telefono",
            "direccion",
            "curso",
            "clase"
        ]