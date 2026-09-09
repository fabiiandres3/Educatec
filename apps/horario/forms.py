from django import forms
from django.utils import timezone

from .models import Periodo, Horario


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

        # Fecha de inicio no puede ser anterior a hoy
        self.fields["fecha_inicio"].widget.attrs["min"] = hoy

        # Fecha final tampoco puede ser anterior a hoy
        self.fields["fecha_fin"].widget.attrs["min"] = hoy

    def clean(self):
        cleaned_data = super().clean()

        numero = cleaned_data.get("numero")
        anio = cleaned_data.get("anio")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        # ==========================================
        # 1. VALIDAR QUE LA FECHA FINAL SEA MAYOR
        # ==========================================

        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:
                self.add_error(
                    "fecha_fin",
                    "La fecha de finalización no puede ser anterior a la fecha de inicio."
                )

        # ==========================================
        # 2. VALIDAR QUE EL PERÍODO NO SE REPITA
        # ==========================================

        if numero and anio:

            existe_periodo = Periodo.objects.filter(
                numero=numero,
                anio=anio
            ).exclude(
                pk=self.instance.pk
            ).exists()

            if existe_periodo:
                self.add_error(
                    "numero",
                    f"El Período {numero} ya existe para el año {anio}."
                )

        # ==========================================
        # 3. VALIDAR QUE LAS FECHAS NO SE CRUCEN
        # ==========================================

        if fecha_inicio and fecha_fin:

            periodos = Periodo.objects.filter(
                fecha_inicio__lte=fecha_fin,
                fecha_fin__gte=fecha_inicio
            ).exclude(
                pk=self.instance.pk
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

    class Meta:
        model = Horario

        fields = [
            "periodo",
            "docente",
            "dia",
            "jornada",
            "hora_inicio",
            "hora_fin",
            "activo",
        ]

        widgets = {

            "periodo": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "docente": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "dia": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "jornada": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "hora_inicio": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),

            "hora_fin": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time"
                }
            ),

            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        jornada = cleaned_data.get("jornada")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if not hora_inicio or not hora_fin:
            return cleaned_data

        # La hora final debe ser mayor
        if hora_fin <= hora_inicio:
            raise forms.ValidationError(
                "La hora de finalización debe ser posterior a la hora de inicio."
            )

        # Jornada mañana: 6:00 AM - 12:00 PM
        if jornada == "manana":

            if hora_inicio.hour < 6:
                raise forms.ValidationError(
                    "La jornada de la mañana comienza a las 6:00 AM."
                )

            if hora_fin.hour > 12 or (
                hora_fin.hour == 12 and hora_fin.minute > 0
            ):
                raise forms.ValidationError(
                    "La jornada de la mañana debe terminar máximo a las 12:00 PM."
                )

        # Jornada tarde: 12:30 PM - 5:00 PM
        elif jornada == "tarde":

            if hora_inicio.hour < 12 or (
                hora_inicio.hour == 12 and hora_inicio.minute < 30
            ):
                raise forms.ValidationError(
                    "La jornada de la tarde comienza a las 12:30 PM."
                )

            if hora_fin.hour > 17:
                raise forms.ValidationError(
                    "La jornada de la tarde debe terminar máximo a las 5:00 PM."
                )

        return cleaned_data