from django import forms
from django.utils import timezone

from apps.user.models import Usuario


# =========================================================
# FORMULARIO DE REGISTRO
# =========================================================

class RegistrarForm(forms.ModelForm):

    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={
            "class": "form-control",
            "type": "date",
            "autocomplete": "bday",
        }),
    )

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data["fecha_nacimiento"]
        if fecha >= timezone.localdate():
            raise forms.ValidationError("La fecha de nacimiento debe ser anterior a hoy.")
        return fecha

    username = forms.CharField(
        label="Documento de identidad",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su documento de identidad",
        }),
    )

    direccion = forms.CharField(
        label="DirecciÃ³n",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su direcciÃ³n",
        }),
    )

    telefono = forms.CharField(
        label="NÃºmero de telÃ©fono",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su nÃºmero de telÃ©fono",
        }),
    )

    password = forms.CharField(
        label="ContraseÃ±a",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su contraseÃ±a"
            }
        )
    )

    password2 = forms.CharField(
        label="Confirmar contraseÃ±a",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirme su contraseÃ±a"
            }
        )
    )

    class Meta:

        model = Usuario

        fields = [
            "username",
            "first_name",
            "last_name",
            "fecha_nacimiento",
            "email",
            "direccion",
            "telefono",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su documento de identidad"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese sus nombres"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese sus apellidos"
                }
            ),

            "fecha_nacimiento": forms.DateInput(format="%Y-%m-%d", attrs={
                    "class": "form-control",
                    "type": "date",
                    "autocomplete": "bday",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su correo electrÃ³nico",
                    "required": True
                }
            ),

            "direccion": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ingrese su direcciÃ³n"}
            ),

            "telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ingrese su nÃºmero de telÃ©fono"}
            ),
        }


    # =====================================================
    # VALIDAR CORREO
    # =====================================================

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if not email:

            raise forms.ValidationError(
                "El correo electrÃ³nico es obligatorio."
            )

        email = email.lower().strip()

        if Usuario.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "Este correo electrÃ³nico ya estÃ¡ registrado."
            )

        return email


    # =====================================================
    # VALIDAR USUARIO
    # =====================================================

    def clean_username(self):

        username = self.cleaned_data.get("username")

        if not username:

            raise forms.ValidationError(
                "El documento de identidad es obligatorio."
            )

        username = username.strip()

        if Usuario.objects.filter(
            documento__iexact=username
        ).exists():

            if self.instance.pk and self.instance.documento == username:
                return username

            raise forms.ValidationError(
                "Este documento ya estÃ¡ registrado."
            )

        return username


    # =====================================================
    # VALIDAR CONTRASEÃ‘AS
    # =====================================================

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")

        password2 = cleaned_data.get("password2")

        if password and password2:

            if password != password2:

                self.add_error(
                    "password2",
                    "Las contraseÃ±as no coinciden."
                )

        return cleaned_data


# =========================================================
# FORMULARIO LOGIN
# =========================================================

class LoginForm(forms.Form):

    username = forms.CharField(
        label="Documento de identidad",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Documento de identidad"
            }
        )
    )

    password = forms.CharField(
        label="ContraseÃ±a",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "ContraseÃ±a"
            }
        )
    )


# =========================================================
# FORMULARIO EDITAR USUARIO
# =========================================================

class EditarUsuarioForm(forms.ModelForm):

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if Usuario.objects.filter(documento__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este documento ya está asociado con otra cuenta.")
        return username

    def clean_fecha_nacimiento(self):
        if self.add_prefix("fecha_nacimiento") not in self.data:
            fecha = self.initial.get("fecha_nacimiento") or self.instance.fecha_nacimiento
        else:
            fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha >= timezone.localdate():
            raise forms.ValidationError("La fecha de nacimiento debe ser anterior a hoy.")
        return fecha

    class Meta:

        model = Usuario

        fields = [
            "username",
            "first_name",
            "last_name",
            "fecha_nacimiento",
            "email",
            "telefono",
            "direccion",
            "rol",
        ]

        labels = {
            "username": "Documento de identidad",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "fecha_nacimiento": "Fecha de nacimiento",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "direccion": "Dirección",
            "rol": "Rol",
        }

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),

            "fecha_nacimiento": forms.DateInput(format="%Y-%m-%d", attrs={"class": "form-control", "type": "date", "autocomplete": "bday"}
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "rol": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),
        }
