from django.urls import path
from . import views


urlpatterns = [

    path(
        "docente/calificaciones/",
        views.calificaciones_docente,
        name="calificaciones_docente"
    ),

    path(
        "docente/calificaciones/editar/<int:calificacion_id>/",
        views.editar_calificacion,
        name="editar_calificacion"
    ),

    path(
        "alumno/calificaciones/",
        views.calificaciones_alumnos,
        name="calificaciones_alumnos"
    ),

    path(
        "guardar/",
        views.guardar_calificacion,
        name="guardar_calificacion"
    ),
    path("actividades/crear/", views.crear_actividad_calificacion, name="crear_actividad_calificacion"),
    path("actividades/guardar-nota/", views.guardar_calificacion_actividad, name="guardar_calificacion_actividad"),

]
