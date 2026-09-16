from django import forms
from django.utils import timezone

from .models import Periodo, Horario
from apps.docentes.models import Docente
from apps.docentes.models import AsignacionDocente


class PeriodoForm(forms.ModelForm):

    class Meta:
        model = Periodo

        fields = [
            "numero",
            "anio",
            "fecha_inicio",
            "fecha_fin",
            "activo",
        ]

        widgets = {
            "fecha_inicio": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hoy = timezone.localdate().isoformat()

        self.fields["fecha_inicio"].widget.attrs["min"] = hoy
        self.fields["fecha_fin"].widget.attrs["min"] = hoy

    def clean(self):
        cleaned_data = super().clean()

        numero = cleaned_data.get("numero")
        anio = cleaned_data.get("anio")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:
                self.add_error(
                    "fecha_fin",
                    "La fecha de finalización no puede ser anterior a la fecha de inicio."
                )

        if numero and anio:

            existe_periodo = (
                Periodo.objects
                .filter(
                    numero=numero,
                    anio=anio
                )
                .exclude(
                    pk=self.instance.pk
                )
                .exists()
            )

            if existe_periodo:
                self.add_error(
                    "numero",
                    f"El Período {numero} ya existe para el año {anio}."
                )

        if fecha_inicio and fecha_fin:

            periodos = (
                Periodo.objects
                .filter(
                    fecha_inicio__lte=fecha_fin,
                    fecha_fin__gte=fecha_inicio
                )
                .exclude(
                    pk=self.instance.pk
                )
            )

            if periodos.exists():

                self.add_error(
                    "fecha_inicio",
                    "Las fechas seleccionadas se cruzan con otro período existente."
                )

                self.add_error(
                    "fecha_fin",
                    "El rango de fechas se cruza con otro período existente."
                )

        return cleaned_data


class HorarioForm(forms.ModelForm):

    docente = forms.ModelChoiceField(
        queryset=Docente.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control"
            }
        ),
        empty_label="Seleccione un docente"
    )

    class Meta:

        model = Horario

        fields = [
            "periodo",
            "docente",
            "curso",
            "clase",
            "dia",
            "jornada",
            "hora_inicio",
            "hora_fin",
        ]