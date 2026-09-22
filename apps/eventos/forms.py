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
            "hora_inicio",
            "hora_fin",
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
                format="%Y-%m-%d",
                attrs={
                    "type": "date"
                }
            ),

            # El selector nativo permite indicar una hora exacta; ``step``
            # habilita todos los minutos, no solo franjas de 30 minutos.
            "hora_inicio": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "step": "60",
                }
            ),

            "hora_fin": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "step": "60",
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        hoy = timezone.localdate()

        # ==========================================
        # FECHA MÍNIMA
        # ==========================================

        self.fields["fecha"].widget.attrs["min"] = hoy.isoformat()

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
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        hoy = timezone.localdate()
        ahora = timezone.localtime().time()

        # ==========================================
        # HORA INICIO < HORA FIN
        # ==========================================

        if hora_inicio and hora_fin:

            if hora_fin <= hora_inicio:

                self.add_error(
                    "hora_fin",
                    "La hora de finalización debe ser posterior a la hora de inicio."
                )

        # ==========================================
        # SI ES HOY
        # ==========================================

        if (
            fecha == hoy
            and hora_inicio
            and hora_inicio <= ahora
        ):

            # Cuando estamos editando el evento actual,
            # permitimos mantener su horario si ya existe.
            if not self.instance.pk:

                self.add_error(
                    "hora_inicio",
                    "No puedes crear un evento con una hora de inicio que ya pasó."
                )

        # ==========================================
        # VALIDACIÓN DE CRUCE
        # ==========================================

        if (
            fecha
            and hora_inicio
            and hora_fin
            and hora_fin > hora_inicio
        ):

            eventos = Evento.objects.filter(
                fecha=fecha,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )

            # Excluir el propio evento cuando estamos editando.
            if self.instance.pk:
                eventos = eventos.exclude(
                    pk=self.instance.pk
                )

            evento_existente = eventos.first()

            if evento_existente:

                self.add_error(
                    "hora_inicio",
                    (
                        f"Este horario se cruza con el evento "
                        f"'{evento_existente.titulo}'."
                    )
                )

                self.add_error(
                    "hora_fin",
                    (
                        f"El evento existente ocupa desde "
                        f"{evento_existente.hora_inicio.strftime('%I:%M %p')} "
                        f"hasta "
                        f"{evento_existente.hora_fin.strftime('%I:%M %p')}."
                    )
                )

        return cleaned_data
