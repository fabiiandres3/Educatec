from django.urls import path
from . import views

urlpatterns = [
    path('listar_alumnos/', views.Listar_alumnos, name='listar_alumnos'),
    path('editar_alumno/<int:alumno_id>/', views.Editar_alumno, name='editar_alumno'),
    path('eliminar_docente/<int:alumno_id>/', views.Eliminar_alumno, name='eliminar_alumno'),
]

