from django.urls import path

from apps.user import views


urlpatterns = [

    # =========================================================
    # PÁGINAS PÚBLICAS
    # =========================================================

    path(
        "",
        views.index,
        name="index"
    ),

    path(
        "prescolar/",
        views.prescolar,
        name="prescolar"
    ),

    path(
        "primaria/",
        views.primaria,
        name="primaria"
    ),

    path(
        "secundaria/",
        views.secundaria,
        name="secundaria"
    ),


    # =========================================================
    # AUTENTICACIÓN
    # =========================================================

    # Login
    path(
        "login/",
        views.iniciar_sesion,
        name="login"
    ),

    # Registro
    path(
        "registro/",
         views.Registrar_usuario,
         name="registrar_usuario"
    ),

    # Cerrar sesión
    path(
        "cerrar/",
        views.cerrar_sesion,
        name="cerrar_sesion"
    ),

    # Redirección automática según el rol
    path(
        "redireccionar/",
        views.redireccionar_por_rol,
        name="redireccionar_por_rol"
    ),


    # =========================================================
    # VERIFICACIÓN DE CORREO
    # =========================================================

    # Esta URL recibe el UID y el TOKEN enviados
    # al correo electrónico durante el registro.
    path(
        "verificar-correo/<uidb64>/<token>/",
        views.verificar_correo,
        name="verificar_correo"
    ),


    # =========================================================
    # USUARIO NORMAL
    # =========================================================

    path(
        "verificacion/",
        views.verificacion,
        name="verificacion"
    ),


    # =========================================================
    # ADMINISTRADOR
    # =========================================================

    path(
        "dashboard_administrador/",
        views.dashboard,
        name="dashboard_administrador"
    ),

    path(
        "listar_usuarios/",
        views.Listar_usuarios,
        name="listar_usuarios"
    ),

    path(
        "editar_usuario/<int:usuario_id>/",
        views.Editar_usuario,
        name="editar_usuario"
    ),

    path(
        "eliminar_usuario/<int:usuario_id>/",
        views.Eliminar_usuario,
        name="eliminar_usuario"
    ),

]