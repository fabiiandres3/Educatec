from django import forms

from .models import Periodo


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
            "numero": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "anio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 2020,
                    "max": 2100,
                    "placeholder": "Ej: 2026",
                }
            ),

            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

        labels = {
            "numero": "Período",
            "anio": "Año académico",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de finalización",
            "activo": "Período activo",
        }

    def clean(self):

        cleaned_data = super().clean()

        numero = cleaned_data.get("numero")
        anio = cleaned_data.get("anio")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        # Validar fechas
        if fecha_inicio and fecha_fin:

            if fecha_fin < fecha_inicio:

                raise forms.ValidationError(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio."
                )

        # Evitar período duplicado
        if numero and anio:

            existe = Periodo.objects.filter(
                numero=numero,
                anio=anio
            )

            if self.instance.pk:

                existe = existe.exclude(
                    pk=self.instance.pk
                )

            if existe.exists():

                raise forms.ValidationError(
                    f"El Período {numero} del año {anio} ya existe."
                )

        # Evitar fechas superpuestas
        if fecha_inicio and fecha_fin and anio:

            periodos = Periodo.objects.filter(
                anio=anio
            )

            if self.instance.pk:

                periodos = periodos.exclude(
                    pk=self.instance.pk
                )

            for periodo in periodos:

                if (
                    fecha_inicio <= periodo.fecha_fin
                    and fecha_fin >= periodo.fecha_inicio
                ):

                    raise forms.ValidationError(
                        f"Las fechas se cruzan con {periodo}. "
                        "Los períodos no pueden superponerse."
                    )

        return cleaned_data