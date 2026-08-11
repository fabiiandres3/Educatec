from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # =========================================================
    # ADMINISTRADOR DE DJANGO
    # =========================================================

    path(
        "admin/",
        admin.site.urls
    ),
    
    path("eventos/", include("apps.eventos.urls")),


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