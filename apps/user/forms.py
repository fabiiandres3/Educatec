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
        widget=forms.DateInput(attrs={
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

    documento = forms.CharField(
        label="Documento de identidad",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su documento de identidad",
        }),
    )

    direccion = forms.CharField(
        label="Dirección",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su dirección",
        }),
    )

    telefono = forms.CharField(
        label="Número de teléfono",
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ingrese su número de teléfono",
        }),
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese su contraseña"
            }
        )
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirme su contraseña"
            }
        )
    )

    class Meta:

        model = Usuario

        fields = [
            "documento",
            "first_name",
            "last_name",
            "fecha_nacimiento",
            "email",
            "direccion",
            "telefono",
        ]

        widgets = {

            "documento": forms.TextInput(
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

            "fecha_nacimiento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "autocomplete": "bday",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su correo electrónico",
                    "required": True
                }
            ),

            "direccion": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ingrese su dirección"}
            ),

            "telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ingrese su número de teléfono"}
            ),
        }


    # =====================================================
    # VALIDAR CORREO
    # =====================================================

    def clean_email(self):

        email = self.cleaned_data.get("email")

        if not email:

            raise forms.ValidationError(
                "El correo electrónico es obligatorio."
            )

        email = email.lower().strip()

        if Usuario.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "Este correo electrónico ya está registrado."
            )

        return email


    # =====================================================
    # VALIDAR USUARIO
    # =====================================================

    def clean_documento(self):

        documento = self.cleaned_data.get("documento")

        if not documento:

            raise forms.ValidationError(
                "El documento de identidad es obligatorio."
            )

        documento = documento.strip()

        if Usuario.objects.filter(
            documento__iexact=documento
        ).exists():

            raise forms.ValidationError(
                "Este documento ya está registrado."
            )

        return documento


    # =====================================================
    # VALIDAR CONTRASEÑAS
    # =====================================================

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")

        password2 = cleaned_data.get("password2")

        if password and password2:

            if password != password2:

                self.add_error(
                    "password2",
                    "Las contraseñas no coinciden."
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
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña"
            }
        )
    )


# =========================================================
# FORMULARIO EDITAR USUARIO
# =========================================================

class EditarUsuarioForm(forms.ModelForm):

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
            "rol",
        ]

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

            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "autocomplete": "bday"}
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
