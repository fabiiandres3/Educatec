from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.listar_eventos,
        name="listar_eventos"
    ),

    path(
        "crear/",
        views.crear_evento,
        name="crear_evento"
    ),

    path(
        "docente/",
        views.eventos_docente,
        name="eventos_docente"
    ),

    path(
        "alumnos/",
        views.eventos_alumnos,
        name="eventos_alumnos"
    ),

]