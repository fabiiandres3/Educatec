from django import forms
from django.utils import timezone

from .models import Periodo, Horario
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
    


from django import forms

from .models import Horario


class HorarioForm(forms.ModelForm):

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

            "curso": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "clase": forms.Select(
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
        }

    def clean(self):

        cleaned_data = super().clean()

        periodo = cleaned_data.get("periodo")
        docente = cleaned_data.get("docente")
        curso = cleaned_data.get("curso")
        clase = cleaned_data.get("clase")

        dia = cleaned_data.get("dia")
        jornada = cleaned_data.get("jornada")

        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        # =====================================================
        # HORAS
        # =====================================================

        if hora_inicio and hora_fin:

            if hora_fin <= hora_inicio:

                raise forms.ValidationError(
                    "La hora de finalización debe ser posterior "
                    "a la hora de inicio."
                )

        # =====================================================
        # JORNADA MAÑANA
        # =====================================================

        if jornada == "manana" and hora_inicio and hora_fin:

            if hora_inicio.hour < 6:

                raise forms.ValidationError(
                    "La jornada de la mañana comienza a las 6:00 AM."
                )

            if hora_fin.hour > 12 or (
                hora_fin.hour == 12
                and hora_fin.minute > 0
            ):

                raise forms.ValidationError(
                    "La jornada de la mañana debe terminar "
                    "máximo a las 12:00 PM."
                )

        # =====================================================
        # JORNADA TARDE
        # =====================================================

        if jornada == "tarde" and hora_inicio and hora_fin:

            if hora_inicio.hour < 12 or (
                hora_inicio.hour == 12
                and hora_inicio.minute < 30
            ):

                raise forms.ValidationError(
                    "La jornada de la tarde comienza a las 12:30 PM."
                )

            if hora_fin.hour > 17:

                raise forms.ValidationError(
                    "La jornada de la tarde debe terminar "
                    "máximo a las 5:00 PM."
                )

        # =====================================================
        # CLASE PERTENECE AL CURSO
        # =====================================================

        if curso and clase:

            if clase.curso_id != curso.id:

                raise forms.ValidationError(
                    "La clase seleccionada no pertenece "
                    "al curso seleccionado."
                )

        # =====================================================
        # DOCENTE TIENE ASIGNADA ESA CLASE
        # =====================================================

        if docente and clase:

            tiene_asignacion = AsignacionDocente.objects.filter(
                docente=docente,
                clase=clase
            ).exists()

            if not tiene_asignacion:

                raise forms.ValidationError(
                    "El docente no tiene asignada "
                    "esta clase."
                )

        # =====================================================
        # PERIODO ACTIVO
        # =====================================================

        if periodo:

            hoy = timezone.localdate()

            if periodo.fecha_fin < hoy:

                raise forms.ValidationError(
                    "No puedes crear un horario para un periodo "
                    "que ya terminó."
                )

                # =====================================================
        # CONFLICTO DEL CURSO / CLASE
        # =====================================================

        if (
            periodo
            and curso
            and clase
            and dia
            and hora_inicio
            and hora_fin
        ):

            conflictos_clase = Horario.objects.filter(
                periodo=periodo,
                curso=curso,
                clase=clase,
                dia=dia,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )

            if self.instance.pk:

                conflictos_clase = conflictos_clase.exclude(
                    pk=self.instance.pk
                )

            if conflictos_clase.exists():

                raise forms.ValidationError(
                    "Esta clase ya tiene un horario asignado "
                    "que se cruza con el horario seleccionado."
                )

        # =====================================================
        # CONFLICTO DEL DOCENTE
        # =====================================================

        if (
            periodo
            and docente
            and dia
            and hora_inicio
            and hora_fin
        ):

            conflictos = Horario.objects.filter(
                periodo=periodo,
                docente=docente,
                dia=dia,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )

            if self.instance.pk:

                conflictos = conflictos.exclude(
                    pk=self.instance.pk
                )

            if conflictos.exists():

                raise forms.ValidationError(
                    "El docente ya tiene otro horario "
                    "en este mismo periodo, día y rango de horas."
                )

        return cleaned_data

        