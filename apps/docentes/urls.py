from django.urls import path
from . import views

urlpatterns = [
    #ADMINISTRADOR
    path('listar_docente/', views.Listar_docentes, name='listar_docentes'),
    path('editar_docente/<int:docente_id>/', views.Editar_docente, name='editar_docente'),
    path('eliminar_docente/<int:docente_id>/', views.Eliminar_docente, name='eliminar_docente'),
]