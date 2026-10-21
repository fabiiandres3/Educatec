from django import forms
from .models import Clases

class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clases
        fields = ['titulo', 'cursos']
        labels = {"titulo": "Nombre de la clase", "cursos": "Cursos asignados"}
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título'
            }),
            'cursos': forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        }
