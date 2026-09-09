from django.urls import path
from . import views


urlpatterns = [

    path(
        "periodos/",
        views.listar_periodos,
        name="listar_periodos"
    ),

    path(
        "periodos/crear/",
        views.crear_periodo,
        name="crear_periodo"
    ),

    path(
        "periodos/<int:pk>/editar/",
        views.editar_periodo,
        name="editar_periodo"
    ),

    path(
        "periodos/<int:pk>/eliminar/",
        views.eliminar_periodo,
        name="eliminar_periodo"
    ),

    path(
        "",
        views.listar_horarios,
        name="listar_horarios"
    ),

    path(
        "crear/",
        views.crear_horario,
        name="crear_horario"
    ),

    path(
        "editar/<int:id>/",
        views.editar_horario,
        name="editar_horario"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_horario,
        name="eliminar_horario"
    ),

]