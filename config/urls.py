from django.contrib import admin
from django.urls import path, include
from apps.alumnos import views as alumnos_views
from apps.user import views as user_views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Rutas del panel propio antes de Django Admin, que captura el prefijo /admin/.
    path("admin/notificaciones-correo/", user_views.notificaciones_correo_admin, name="notificaciones_correo_admin"),
    path(
        "admin/acudientes/relacion/<int:relacion_id>/editar/",
        alumnos_views.editar_relacion_acudiente,
        name="editar_relacion_acudiente",
    ),
    path(
        "admin/acudientes/relacion/<int:relacion_id>/eliminar/",
        alumnos_views.eliminar_relacion_acudiente,
        name="eliminar_relacion_acudiente",
    ),
    path(
        "admin/acudientes/",
        alumnos_views.administrar_acudientes,
        name="administrar_acudientes",
    ),

    # =========================================================
    # ADMINISTRADOR DE DJANGO
    # =========================================================

    path(
        "admin/",
        admin.site.urls
    ),
    
    path("", include("apps.eventos.urls")),


    # =========================================================
    # APLICACIONES
    # =========================================================

    path(
        "",
        include("apps.alumnos.urls")
    ),

    path(
        "",
        include("apps.clases.urls")
    ),

    path(
        "",
        include("apps.cursos.urls")
    ),

    path(
        "",
        include("apps.docentes.urls")
    ),

    path(
        "",
        include("apps.tareas.urls")
    ),

    path(
        "",
        include("apps.user.urls")
    ),

    path(
        "",
        include("apps.paneles.urls")
    ),

    path(
            "",
            include("apps.horario.urls")
        ),
    
    path(
    "",
    include("apps.calificaciones.urls")
),

    path(
        "",
        include("apps.boletin.urls")
    ),


    # =========================================================
    # DJANGO ALLAUTH
    # LOGIN / REGISTRO / LOGOUT / GOOGLE / RECUPERACIÓN
    # =========================================================

    path(
        "accounts/",
        include("allauth.urls")
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
