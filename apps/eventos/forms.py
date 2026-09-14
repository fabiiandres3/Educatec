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
                }
            ),

            "hora": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hoy = timezone.localdate()

        # No permitir fechas anteriores a hoy
        self.fields["fecha"].widget.attrs["min"] = hoy.isoformat()

        # Crear opciones de hora cada 30 minutos
        opciones_hora = [
            ("", "Selecciona una hora")
        ]

        for hora in range(0, 24):
            for minuto in (0, 30):

                valor = f"{hora:02d}:{minuto:02d}"
                texto = timezone.datetime(
                    2000, 1, 1, hora, minuto
                ).strftime("%I:%M %p")

                opciones_hora.append((valor, texto))

        self.fields["hora"].choices = opciones_hora

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")

        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError(
                "No puedes crear un evento en una fecha que ya pasó."
            )

        return fecha

    def clean(self):
        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        hoy = timezone.localdate()
        ahora = timezone.localtime().time()

        if fecha == hoy and hora and hora <= ahora:
            self.add_error(
                "hora",
                "No puedes crear un evento con una hora que ya pasó."
            )

        return cleaned_data
