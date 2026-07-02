from django import forms
from apps.docente.models import Docente

class DocenteForm(forms.ModelForm):

    class Meta:
        model = Docente
        fields = [
            "usuario",
            "telefono",
            "direccion",
            "clase",
            "curso",
        ]