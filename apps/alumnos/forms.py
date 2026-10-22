from django import forms
from .models import Alumnos, Acudiente, AcudienteAlumno
from apps.user.models import Usuario


class AlumnoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curso"].empty_label = "Seleccione un curso"

    class Meta:
        model = Alumnos
        exclude = ["usuario", "fecha_nacimiento", "telefono", "direccion", "clase"]
        labels = {
            "curso": "Curso",
            "fecha_ingreso": "Fecha de ingreso",
            "activo": "Estado activo",
        }
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "fecha_ingreso": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Código del alumno"
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono"
            }),
            "direccion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Dirección"
            }),
            "nombre_acudiente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del acudiente"
            }),
            "telefono_acudiente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono del acudiente"
            }),
            "parentesco_acudiente": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Parentesco"
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }


class CrearAcudienteForm(forms.Form):
    username = forms.CharField(
        label="Documento de identidad",
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    nombres = forms.CharField(
        label="Nombres",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    apellidos = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    direccion = forms.CharField(
        label="Dirección",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    )
    password = forms.CharField(
        label="Contraseña inicial",
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if Usuario.objects.filter(documento__iexact=username).exists() or Usuario.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError("Ya existe un usuario con ese documento.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo.")
        return email


class AlumnoCursoSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        alumno = getattr(value, "instance", None)
        if alumno:
            option["attrs"]["data-course-id"] = str(alumno.curso_id or "")
            option["attrs"]["data-course-name"] = str(alumno.curso or "Sin curso")
            option["attrs"]["data-search"] = f"{alumno.usuario.get_full_name()} {alumno.usuario.documento or ''}"
            option["attrs"]["data-document"] = str(alumno.usuario.documento or "")
        return option

class AcudienteAlumnoForm(forms.ModelForm):
    parentesco = forms.ChoiceField(
        label="Parentesco",
        choices=[("Acudiente", "Acudiente"), ("Madre", "Madre"), ("Padre", "Padre")],
        initial="Acudiente",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    class Meta:
        model = AcudienteAlumno
        fields = ["alumno", "parentesco", "es_principal", "autorizado"]
        labels = {
            "alumno": "Alumno",
            "parentesco": "Parentesco",
            "es_principal": "Acudiente principal",
            "autorizado": "Autorizado",
        }
        widgets = {
            "alumno": AlumnoCursoSelect(attrs={"class": "form-select guardian-source-input"}),
            "parentesco": forms.Select(attrs={"class": "form-select"}),
            "es_principal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "autorizado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acudiente"] = forms.ModelChoiceField(
            label="Acudiente",
            empty_label="Seleccione una opción",
            queryset=Usuario.objects.filter(
            rol__nombre__iexact="acudiente"
            ).order_by("last_name", "first_name", "documento"),
            widget=forms.Select(attrs={"class": "form-select"}),
        )
        self.fields["acudiente"].label_from_instance = lambda usuario: (
            f"{usuario.get_full_name() or 'Sin nombre'} · {usuario.documento or 'Sin documento'}"
        )
        self.order_fields(["acudiente", "alumno", "parentesco", "es_principal", "autorizado"])
        if self.instance and self.instance.pk:
            self.initial["acudiente"] = self.instance.acudiente.usuario
            self.initial["alumno"] = self.instance.alumno
        self.fields["alumno"].empty_label = "Seleccione una opción"
        self.fields["alumno"].queryset = Alumnos.objects.select_related("usuario").order_by(
            "usuario__last_name", "usuario__first_name"
        )

    def clean(self):
        cleaned_data = super().clean()
        usuario_acudiente = cleaned_data.get("acudiente")
        alumno = cleaned_data.get("alumno")
        if usuario_acudiente and alumno:
            relaciones = AcudienteAlumno.objects.filter(alumno=alumno)
            if self.instance and self.instance.pk:
                relaciones = relaciones.exclude(pk=self.instance.pk)
            if relaciones.exists():
                self.add_error("alumno", "Este alumno ya está relacionado con un acudiente.")
        return cleaned_data

    def save(self, commit=True):
        relacion = super().save(commit=False)
        usuario_acudiente = self.cleaned_data["acudiente"]
        perfil, _ = Acudiente.objects.get_or_create(
            usuario=usuario_acudiente,
            defaults={
                "telefono": usuario_acudiente.telefono,
                "direccion": usuario_acudiente.direccion,
            },
        )
        relacion.acudiente = perfil
        if commit:
            relacion.save()
            self.save_m2m()
        return relacion
