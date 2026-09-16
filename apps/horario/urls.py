from django.urls import path

from . import views


urlpatterns = [

    # =========================================================
    # PERIODOS
    # =========================================================

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


    # =========================================================
    # HORARIOS
    # =========================================================

    path(
        "listar_horario",
        views.listar_horarios,
        name="listar_horarios"
    ),

    path(
        "crear/",
        views.crear_horario,
        name="crear_horario"
    ),

    path(
        "eliminar/<int:id>/",
        views.eliminar_horario,
        name="eliminar_horario"
    ),


    # =========================================================
    # PLANIFICADOR VISUAL
    # =========================================================

    path(
        "listar_horario/",
        views.listar_horario,
        name="listar_horario"
    ),

    path(
        "crear_horario/",
        views.crear_horario,
        name="crear_horario"
    ),

    path(
        "crear/<int:periodo_id>/<int:curso_id>/",
        views.crear_horario_curso,
        name="crear_horario_curso",
    ),

    path(
        "editar/<int:periodo_id>/<int:curso_id>/",
        views.editar_horario,
        name="editar_horario"
    ),


    # =========================================================
    # AJAX
    # =========================================================

    path(
        "guardar_horario_ajax/",
        views.guardar_horario_ajax,
        name="guardar_horario_ajax",
    ),

]