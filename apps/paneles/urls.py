from django.urls import path
from . import views


urlpatterns = [

    # =========================================================
    # DOCENTE
    # =========================================================

    path(
        "docente/",
        views.dashboard_docente,
        name="dashboard_docente"
    ),

    path(
        "docente/cursos/",
        views.cursos_docente,
        name="cursos_docente"
    ),

    path(
        "docente/calificaciones/",
        views.calificaciones_docente,
        name="calificaciones_docente"
    ),

    path(
        "docente/asistencia/",
        views.asistencia_docente,
        name="asistencia_docente"
    ),

    path(
        "docente/asistencia/historial/",
        views.historial_asistencia,
        name="historial_asistencia"
    ),

    path(
        "docente/asistencia/guardar/",
        views.guardar_asistencia,
        name="guardar_asistencia"
    ),

    path(
        "docente/configuracion/",
        views.configuracion_docente,
        name="configuracion_docente"
    ),


    # =========================================================
    # ALUMNOS
    # =========================================================

    path(
        "alumno/",
        views.dashboard_alumnos,
        name="dashboard_alumnos"
    ),

    path(
        "alumno/materias/",
        views.materias_alumnos,
        name="materias_alumnos"
    ),

    path(
        "alumno/calificaciones/",
        views.calificaciones_alumnos,
        name="calificaciones_alumnos"
    ),

    path(
        "alumno/asistencia/",
        views.asistencia_alumnos,
        name="asistencia_alumnos"
    ),

    path(
        "alumno/logros/",
        views.logros_alumnos,
        name="logros_alumnos"
    ),

    path(
        "alumno/configuracion/",
        views.configuracion_alumnos,
        name="configuracion_alumnos"
    ),

]