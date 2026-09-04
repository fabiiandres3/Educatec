from django.urls import path

from . import views


urlpatterns = [

    path(
        "eventos/listar_eventos",
        views.listar_eventos,
        name="listar_eventos"
    ),

    path(
        "eventos/crear/",
        views.crear_evento,
        name="crear_evento"
    ),

    path(
        "eventos/<int:evento_id>/editar/",
        views.editar_evento,
        name="editar_evento"
    ),

    path(
        "eventos/<int:evento_id>/eliminar/",
        views.eliminar_evento,
        name="eliminar_evento"
    ),

    path(
        "eventos/<int:id>/",
        views.detalle_evento,
        name="detalle_evento"
    ),

    path( "eventos/alumno/", views.listar_eventos_alumno, name="listar_eventos_alumno" ), 
    path( "eventos/docente/", views.listar_eventos_docente, name="listar_eventos_docente" ),

]