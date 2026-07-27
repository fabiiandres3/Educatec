from django.urls import path

from . import views


urlpatterns = [

    # =========================================================
    # DASHBOARD DOCENTE
    # =========================================================

    path(
        "dashboard_docente/",
        views.dashboard_docente,
        name="dashboard_docente"
    ),

    path(
        "docente_cursos/",
        views.cursos_docente,
        name="cursos_docente"
    ),

    path(
        "docente_calificaciones/",
        views.calificaciones_docente,
        name="calificaciones_docente"
    ),

    path(
        "docente_asistencia/",
        views.asistencia_docente,
        name="asistencia_docente"
    ),

    path(
        "docente_asistencia/historial/",
        views.historial_asistencia,
        name="historial_asistencia"
    ),

    path(
        "docente_asistencia/guardar/",
        views.guardar_asistencia,
        name="guardar_asistencia"
    ),

    path(
        "docente_configuracion/",
        views.configuracion_docente,
        name="configuracion_docente"
    ),


    # =========================================================
    # DASHBOARD ALUMNO
    # =========================================================

    path(
        "dashboard_alumnos/",
        views.dashboard_alumnos,
        name="dashboard_alumnos"
    ),

    path(
        "dashboard_alumnos/materias/",
        views.materias_alumnos,
        name="materias_alumnos"
    ),

    path(
        "dashboard_alumnos/calificaciones/",
        views.calificaciones_alumnos,
        name="calificaciones_alumnos"
    ),

    path(
        "dashboard_alumnos/asistencia/",
        views.asistencia_alumnos,
        name="asistencia_alumnos"
    ),

    path(
        "dashboard_alumnos/logros/",
        views.logros_alumnos,
        name="logros_alumnos"
    ),

    path(
        "dashboard_alumnos/configuracion/",
        views.configuracion_alumnos,
        name="configuracion_alumnos"
    ),

]