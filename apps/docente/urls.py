from django.urls import path
from . import views

urlpatterns = [
    path("docentes/", views.listar_docentes, name="listar_docentes"),
    path("crear_docente/<int:docente_id>/", views.crear_docente, name="crear_docente"),
    path("editar_docente/<int:docente_id>/", views.editar_docente, name="editar_docente"),
    path("eliminar_docente/<int:docente_id>/", views.eliminar_docente, name="eliminar_docente"),
]