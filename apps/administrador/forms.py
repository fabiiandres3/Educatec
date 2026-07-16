from django import forms
from apps.docentes.models import Docente

class RegistrarDocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = [
            "telefono",
            "direccion",
            "curso",
            "clase"
        ]


class EditarDocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = [
            "telefono",
            "direccion",
            "curso",
            "clase"
        ]