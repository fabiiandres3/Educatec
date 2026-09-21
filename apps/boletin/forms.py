from django import forms

from .models import ContenidoPedagogico, ObservacionBoletin


class ContenidoPedagogicoForm(forms.ModelForm):
    class Meta:
        model = ContenidoPedagogico
        fields = ["competencias", "contenidos", "logros", "dificultades_generales", "recomendaciones"]
        widgets = {
            field: forms.Textarea(attrs={"class": "form-control", "rows": 3})
            for field in fields
        }


class ObservacionBoletinForm(forms.ModelForm):
    class Meta:
        model = ObservacionBoletin
        fields = ["observacion", "publicado"]
        widgets = {
            "observacion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "publicado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
