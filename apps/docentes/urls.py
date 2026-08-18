from django.urls import path
from . import views

urlpatterns = [
    #ADMINISTRADOR
    path('listar_docente/', views.Listar_docentes, name='listar_docentes'),
    path('editar_docente/<int:docente_id>/', views.Editar_docente, name='editar_docente'),
    path('eliminar_docente/<int:docente_id>/', views.Eliminar_docente, name='eliminar_docente'),
    path(
        'listar_tareas_docentes/',
        views.listar_tareas,
        name='listar_tareas_docentes'
    ),

    path(
        "crear_tarea_docente/",
        views.crear_tareas_docente,
        name="crear_tarea_docente"
    ),

    path(
        "editar_tarea_docente/<int:tarea_id>/",
        views.editar_tarea_docente,
        name="editar_tarea_docente",
    ),

    path(
        "eliminar_tarea_docente/<int:tarea_id>/",
        views.eliminar_tarea_docente,
        name="eliminar_tarea_docente"
    ),


   path(
        "respuesta_alumnos/<int:tarea_id>/",
        views.respuesta_alumnos,
        name="respuesta_alumnos",
    ),

    path(
        "ver_respuestas/<int:tarea_id>/<int:alumno_id>/",
        views.ver_respuestas,
        name="ver_respuestas",
    ),
]