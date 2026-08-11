from django import forms

from .models import Evento


class EventoForm(forms.ModelForm):

    class Meta:
        model = Evento

        fields = [
            "titulo",
            "tipo",
            "fecha",
            "hora",
            "descripcion",
            "imagen",
            "video",
            "publico",
            "publicado",
        ]

        widgets = {
            "titulo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Título del evento",
                }
            ),

            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "fecha": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "hora": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Descripción del evento...",
                }
            ),

            "imagen": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "video": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://youtube.com/...",
                }
            ),

            "publico": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "publicado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }