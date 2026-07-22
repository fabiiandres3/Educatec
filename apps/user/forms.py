from django import forms

from apps.user.models import Usuario


# =========================================================
# FORMULARIO DE REGISTRO
# =========================================================

class RegistrarForm(forms.ModelForm):

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
            "username",
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su usuario"
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

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingrese su correo electrónico",
                    "required": True
                }
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

    def clean_username(self):

        username = self.cleaned_data.get("username")

        if not username:

            raise forms.ValidationError(
                "El nombre de usuario es obligatorio."
            )

        username = username.strip()

        if Usuario.objects.filter(
            username__iexact=username
        ).exists():

            raise forms.ValidationError(
                "Este nombre de usuario ya está registrado."
            )

        return username


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
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Usuario"
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

    class Meta:

        model = Usuario

        fields = [
            "username",
            "first_name",
            "last_name",
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