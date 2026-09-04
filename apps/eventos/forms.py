from django import forms
from django.utils import timezone

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
                    "type": "date",
                    "min": timezone.localdate().isoformat()
                }
            ),

            "hora": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")

        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError(
                "No puedes crear un evento en una fecha que ya pasó."
            )

        return fecha

