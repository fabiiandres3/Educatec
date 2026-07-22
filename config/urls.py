from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views


urlpatterns = [

    # =========================================================
    # ADMINISTRADOR DE DJANGO
    # =========================================================

    path(
        "admin/",
        admin.site.urls
    ),


    # =========================================================
    # APLICACIÓN USER
    # =========================================================

    # Aquí están:
    # - Login
    # - Registro
    # - Logout
    # - Verificación de correo
    # - Redirección por rol
    # - Dashboard administrador
    # - Gestión de usuarios

    path(
        "",
        include("apps.user.urls")
    ),


    # =========================================================
    # PANELES
    # =========================================================

    # Aquí están:
    # - Dashboard docente
    # - Dashboard alumno
    # - Vistas de docente
    # - Vistas de alumno

    path(
        "",
        include("apps.paneles.urls")
    ),


    # =========================================================
    # DJANGO ALLAUTH / GOOGLE
    # =========================================================

    path(
        "accounts/",
        include("allauth.urls")
    ),


    # =========================================================
    # RECUPERACIÓN DE CONTRASEÑA
    # =========================================================

    # Paso 1:
    # Usuario introduce su correo electrónico.

    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(

            template_name=(
                "login/password_reset.html"
            ),

            email_template_name=(
                "login/password_reset_email.html"
            ),

            subject_template_name=(
                "login/password_reset_subject.txt"
            ),

            success_url=(
                "/password_reset/done/"
            )

        ),

        name="password_reset"
    ),


    # Paso 2:
    # Se informa al usuario que se envió
    # el correo de recuperación.

    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(

            template_name=(
                "login/password_reset_done.html"
            )

        ),

        name="password_reset_done"
    ),


    # Paso 3:
    # El usuario entra al enlace recibido
    # en su correo.

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(

            template_name=(
                "login/password_reset_confirm.html"
            ),

            success_url=(
                "/reset/done/"
            )

        ),

        name="password_reset_confirm"
    ),


    # Paso 4:
    # Se informa que la contraseña
    # fue cambiada correctamente.

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(

            template_name=(
                "login/password_reset_complete.html"
            )

        ),

        name="password_reset_complete"
    ),

]


# =========================================================
# ARCHIVOS MEDIA EN DESARROLLO
# =========================================================

if settings.DEBUG:

    urlpatterns += static(

        settings.MEDIA_URL,

        document_root=settings.MEDIA_ROOT

    )