from django import forms

from .models import Evento


class EventoForm(forms.ModelForm):

    class Meta:
        model = Evento

        fields = [
            "titulo",
            "descripcion",
            "imagen",
            "video",
            "tipo",
            "publico",
            "fecha",
            "hora",
        ]

        widgets = {

            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Título del evento"
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Descripción del evento"
                }
            ),

            "video": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://youtube.com/..."
                }
            ),

            "tipo": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "publico": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "fecha": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "hora": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),

            "lugar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Lugar del evento"
                }
            ),

            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }