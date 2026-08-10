from django.urls import path
from . import views


urlpatterns = [

    # ==========================================
    # CURSOS + ALUMNOS
    # ==========================================

    path(
        "listar_cursos/",
        views.listar_cursos,
        name="listar_cursos"
    ),


    # ==========================================
    # SOLO ALUMNOS
    # ==========================================

    path(
        "listar_alumnos/",
        views.listar_alumnos,
        name="listar_alumnos"
    ),


    # ==========================================
    # CREAR CURSO
    # ==========================================

    path(
        "crear_curso/",
        views.Crear_curso,
        name="crear_curso"
    ),


    # ==========================================
    # EDITAR CURSO
    # ==========================================

    path(
        "editar_curso/<int:curso_id>/",
        views.Editar_curso,
        name="editar_curso"
    ),


    # ==========================================
    # ELIMINAR CURSO
    # ==========================================

    path(
        "eliminar_curso/<int:curso_id>/",
        views.Eliminar_curso,
        name="eliminar_curso"
    ),

    path(
        "filtrar-alumnos/",
        views.filtrar_alumnos,
        name="filtrar_alumnos"
    ),


    # ==========================================
    # ASIGNAR ALUMNO A CURSO
    # ==========================================

    path(
        "asignar_alumno/<int:alumno_id>/<int:curso_id>/",
        views.asignar_alumno_curso,
        name="asignar_alumno_curso"
    ),

]