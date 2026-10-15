from django import forms
from .models import Alumnos, Acudiente, AcudienteAlumno
from apps.user.models import Usuario


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumnos
        exclude = ["usuario", "fecha_nacimiento"]
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
    documento = forms.CharField(
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

    def clean_documento(self):
        documento = self.cleaned_data["documento"].strip()
        if Usuario.objects.filter(documento__iexact=documento).exists() or Usuario.objects.filter(
            username__iexact=documento
        ).exists():
            raise forms.ValidationError("Ya existe un usuario con ese documento.")
        return documento

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo.")
        return email


class AcudienteAlumnoForm(forms.ModelForm):
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
            "alumno": forms.Select(attrs={"class": "form-select"}),
            "parentesco": forms.TextInput(attrs={"class": "form-control"}),
            "es_principal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "autorizado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acudiente"] = forms.ModelChoiceField(
            label="Acudiente",
            queryset=Usuario.objects.filter(
            rol__nombre__iexact="acudiente"
            ).order_by("last_name", "first_name", "documento"),
            widget=forms.Select(attrs={"class": "form-select"}),
        )
        self.fields["acudiente"].label_from_instance = lambda usuario: (
            f"{usuario.get_full_name() or 'Sin nombre'} · {usuario.documento or 'Sin documento'}"
        )
        self.order_fields(["acudiente", "alumno", "parentesco", "es_principal", "autorizado"])
        self.fields["alumno"].queryset = Alumnos.objects.select_related("usuario").order_by(
            "usuario__last_name", "usuario__first_name"
        )

    def clean(self):
        cleaned_data = super().clean()
        usuario_acudiente = cleaned_data.get("acudiente")
        alumno = cleaned_data.get("alumno")
        if usuario_acudiente and alumno:
            perfil = Acudiente.objects.filter(usuario=usuario_acudiente).first()
            if perfil and AcudienteAlumno.objects.filter(acudiente=perfil, alumno=alumno).exists():
                self.add_error("alumno", "Este acudiente ya está relacionado con el alumno seleccionado.")
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
