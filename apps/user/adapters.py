from datetime import date

from allauth.socialaccount.adapter import (
    DefaultSocialAccountAdapter
)
from allauth.account.forms import SignupForm as AccountSignupFormBase
from allauth.socialaccount.forms import SignupForm
from django import forms

from apps.user.models import (
    Usuario,
    Roles
)


class AccountSignupForm(AccountSignupFormBase):
    """Incluye la fecha de nacimiento en el registro estándar de Allauth."""

    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date", "autocomplete": "bday"}),
    )

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data["fecha_nacimiento"]
        if fecha >= date.today():
            raise forms.ValidationError("La fecha de nacimiento debe ser anterior a hoy.")
        return fecha

    def custom_signup(self, request, user):
        user.fecha_nacimiento = self.cleaned_data["fecha_nacimiento"]
        user.rol, _ = Roles.objects.get_or_create(nombre__iexact="usuario", defaults={"nombre": "Usuario"})
        user.save(update_fields=["fecha_nacimiento", "rol"])


class GoogleSignupForm(SignupForm):
    """Pide y guarda los nombres durante el alta social de Google."""

    first_name = forms.CharField(label="Nombres", max_length=100, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=100, required=True)
    direccion = forms.CharField(label="Dirección", max_length=255, required=True)
    telefono = forms.CharField(label="Número de teléfono", max_length=30, required=True)
    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=True,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
            "autocomplete": "bday",
        }),
    )
    password1 = forms.CharField(
        label="Contraseña",
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Crea una contraseña",
            "autocomplete": "new-password",
        }),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Repite la contraseña",
            "autocomplete": "new-password",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Documento de identidad"
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Ingrese su documento de identidad",
        })
        self.initial["username"] = ""
        orden_campos = [
            nombre for nombre in self.fields
            if nombre not in ("password1", "password2")
        ]
        self.order_fields(orden_campos + ["password1", "password2"])

    def clean(self):
        cleaned_data = super().clean()
        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")
        if fecha_nacimiento and fecha_nacimiento >= date.today():
            self.add_error("fecha_nacimiento", "La fecha de nacimiento debe ser anterior a hoy.")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned_data

    def custom_signup(self, request, user):
        user.documento = self.cleaned_data["username"].strip()
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.direccion = self.cleaned_data["direccion"]
        user.telefono = self.cleaned_data["telefono"]
        user.fecha_nacimiento = self.cleaned_data["fecha_nacimiento"]
        user.set_password(self.cleaned_data["password1"])
        user.save(update_fields=[
            "documento", "first_name", "last_name", "direccion", "telefono",
            "fecha_nacimiento", "password"
        ])


class CustomSocialAccountAdapter(
    DefaultSocialAccountAdapter
):

    def pre_social_login(
        self,
        request,
        sociallogin
    ):

        # =====================================================
        # SI GOOGLE YA ESTÁ CONECTADO
        # =====================================================

        if sociallogin.is_existing:

            return


        # =====================================================
        # OBTENER CORREO DE GOOGLE
        # =====================================================

        email = (
            sociallogin.account.extra_data.get(
                "email"
            )
        )


        if not email:

            return


        # =====================================================
        # BUSCAR USUARIO EXISTENTE
        # =====================================================

        try:

            usuario = Usuario.objects.get(

                email__iexact=email

            )


            # =================================================
            # CONECTAR GOOGLE AL USUARIO EXISTENTE
            # =================================================

            sociallogin.connect(

                request,

                usuario

            )


        except Usuario.DoesNotExist:

            pass


    def populate_user(
        self,
        request,
        sociallogin,
        data
    ):

        usuario = super().populate_user(

            request,

            sociallogin,

            data

        )


        # =====================================================
        # DATOS DE GOOGLE
        # =====================================================

        email = data.get(
            "email",
            ""
        )

        first_name = data.get(
            "first_name",
            ""
        )

        last_name = data.get(
            "last_name",
            ""
        )


        usuario.email = email

        usuario.first_name = first_name

        usuario.last_name = last_name


        # =====================================================
        # ASIGNAR ROL USUARIO
        # =====================================================

        usuario.rol, _ = Roles.objects.get_or_create(
            nombre__iexact="usuario",
            defaults={"nombre": "Usuario"},
        )


        # =====================================================
        # GOOGLE YA VERIFICÓ EL CORREO
        # =====================================================

        usuario.is_active = True


        return usuario
