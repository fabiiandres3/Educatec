from django.urls import path
from . import views


urlpatterns = [

    # ========================================================
    # TAREAS
    # ========================================================

    path(
        "tareas/",
        views.Listar_tareas,
        name="listar_tareas"
    ),

    path(
        "crear_tarea/",
        views.Crear_tarea,
        name="crear_tarea"
    ),

    path(
        "editar_tarea/<int:tarea_id>/",
        views.Editar_tarea,
        name="editar_tarea"
    ),

    path(
        "eliminar_tarea/<int:tarea_id>/",
        views.Eliminar_tarea,
        name="eliminar_tarea"
    ),

    path(
        "detalle_tarea/<int:tarea_id>/",
        views.Detalle_tarea,
        name="detalle_tarea"
    ),

    # ========================================================
    # DOCENTE - VER RESPUESTA DEL ESTUDIANTE
    # ========================================================

    path(
        "ver_respuesta/<int:tarea_id>/<int:alumno_id>/",
        views.Ver_respuesta,
        name="ver_respuesta"
    ),

    # ========================================================
    # DOCENTE - EVALUAR RESPUESTA
    # ========================================================

    path(
        "evaluar_respuesta/<int:tarea_id>/",
        views.Evaluar_respuesta,
        name="evaluar_respuesta"
    ),
]