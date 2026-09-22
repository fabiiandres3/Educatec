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
            "periodo",
            "clase",
            "curso",
        ]

        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Título de la tarea",
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descripción de la tarea",
            }),

            "fecha_entrega": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),

            "periodo": forms.Select(attrs={
                "class": "form-select",
            }),

            "clase": forms.Select(attrs={
                "class": "form-select",
            }),

            "curso": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fecha mínima: hoy
        fecha_hoy = timezone.localdate().isoformat()

        self.fields["fecha_entrega"].widget.attrs["min"] = fecha_hoy

    def clean_fecha_entrega(self):
        fecha = self.cleaned_data.get("fecha_entrega")

        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError(
                "No puedes seleccionar una fecha anterior a hoy."
            )

        return fecha