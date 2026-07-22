from allauth.socialaccount.adapter import (
    DefaultSocialAccountAdapter
)

from apps.user.models import (
    Usuario,
    Roles
)


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

        try:

            rol_usuario = Roles.objects.get(

                nombre__iexact="usuario"

            )

            usuario.rol = rol_usuario


        except Roles.DoesNotExist:

            usuario.rol = None


        # =====================================================
        # GOOGLE YA VERIFICÓ EL CORREO
        # =====================================================

        usuario.is_active = True


        return usuario