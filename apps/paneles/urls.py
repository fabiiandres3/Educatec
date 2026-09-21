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



    # =========================================================
    # ASISTENCIA DOCENTE
    # =========================================================

    path(
        "docente/asistencia/",
        views.asistencia_docente,
        name="asistencia_docente"
    ),

    path(
        "docente/asistencia/datos/",
        views.obtener_datos_asistencia,
        name="obtener_datos_asistencia"
    ),

    path(
        "docente/asistencia/guardar/",
        views.guardar_asistencia_ajax,
        name="guardar_asistencia_ajax"
    ),

    path(
        "docente/asistencia/historial/",
        views.historial_asistencia,
        name="historial_asistencia"
    ),

    # =========================================================
    # DOCENTE - OTROS
    # =========================================================

    path(
        "docente/configuracion/",
        views.configuracion_docente,
        name="configuracion_docente"
    ),

    path(
        "docente/carga-academica/",
        views.carga_academica,
        name="carga_academica"
    ),

    path(
        "docente/horarios/",
        views.horarios_docente,
        name="horarios_docente"
    ),

    path(
        "docente/horarios/<int:periodo_id>/<int:curso_id>/",
        views.detalle_horario_docente,
        name="detalle_horario_docente"
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

    path(
        "alumno/horarios/",
        views.horarios_alumnos,
        name="horarios_alumnos"
    ),

    # =========================================================
    # ACUDIENTE
    # =========================================================

    path(
        "acudiente/",
        views.dashboard_acudiente,
        name="dashboard_acudiente"
    ),

    path(
        "acudiente/alumno/<int:alumno_id>/",
        views.detalle_alumno_acudiente,
        name="detalle_alumno_acudiente"
    ),

]