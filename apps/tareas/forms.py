from django import forms
from django.utils import timezone

from .models import Tareas, Pregunta


class TareasForm(forms.ModelForm):

    class Meta:
        model = Tareas

        fields = [
            "titulo",
            "descripcion",
            "fecha_entrega",
            "clase",
            "curso",
        ]

        widgets = {

            "fecha_entrega": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "min": timezone.localdate().isoformat(),
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "rows": 1,
                    "cols": -20,
                    "class": "form-control",
                }
            ),
        }

    def clean_fecha_entrega(self):

        fecha_entrega = self.cleaned_data.get("fecha_entrega")

        if fecha_entrega and fecha_entrega < timezone.localdate():
            raise forms.ValidationError(
                "No puedes seleccionar una fecha de entrega que ya pasó."
            )

        return fecha_entrega


class PreguntasForm(forms.ModelForm):

    class Meta:
        model = Pregunta

        fields = [
            "descripcion",
            "tipo",
            "puntaje",  
        ]