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


]