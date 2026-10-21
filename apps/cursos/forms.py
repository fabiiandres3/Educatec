from django import forms
from .models import Cursos
from apps.clases.models import Clases
from apps.docentes.models import AsignacionDocente, Docente

class CursosForm(forms.ModelForm):
    clases = forms.ModelMultipleChoiceField(
        label="Clases del curso",
        queryset=Clases.objects.none(),
        required=False,
        help_text="Selecciona las clases que formarán parte de este curso.",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "class-option-check"}),
    )
    docentes = forms.ModelMultipleChoiceField(
        label="Docentes del curso",
        queryset=Docente.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "teacher-option-check"}),
    )

    class Meta:
        model = Cursos
        fields = ['nombre', 'imagen']

    def __init__(self, *args, **kwargs):
        kwargs.pop("incluir_clases", None)
        super().__init__(*args, **kwargs)
        self.fields["clases"].queryset = Clases.objects.order_by("titulo")
        self.fields["docentes"].queryset = Docente.objects.select_related("usuario").order_by(
            "usuario__first_name", "usuario__last_name", "usuario__username"
        )
        if self.instance and self.instance.pk:
            self.fields["clases"].initial = self.instance.clases.all()
            self.fields["docentes"].initial = Docente.objects.filter(
                asignaciones__curso=self.instance,
                asignaciones__clase__isnull=True,
            ).distinct()
        self.fields.pop("imagen", None)

    def save(self, commit=True):
        curso = super().save(commit=commit)
        if commit and "clases" in self.cleaned_data:
            curso.clases.set(self.cleaned_data["clases"])
        if commit and "docentes" in self.cleaned_data:
            seleccionados = self.cleaned_data["docentes"]
            asignaciones_directas = AsignacionDocente.objects.filter(
                curso=curso,
                clase__isnull=True,
            )
            asignaciones_directas.exclude(docente__in=seleccionados).delete()
            existentes = set(asignaciones_directas.filter(
                docente__in=seleccionados
            ).values_list("docente_id", flat=True))
            AsignacionDocente.objects.bulk_create([
                AsignacionDocente(docente=docente, curso=curso)
                for docente in seleccionados
                if docente.pk not in existentes
            ])
        return curso
