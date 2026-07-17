from django.urls import path
from . import views

urlpatterns = [
    path('listar_docentes/', views.Listar_docentes, name='listar_docentes'),
    path('editar_docente/<int:docente_id>/', views.Editar_docente, name='editar_docente'),
    path('eliminar_docente/<int:docente_id>/', views.Eliminar_docente, name='eliminar_docente'),
    #USUARIOS-ADMIN
    path('listar_usuarios/', views.Listar_usuarios, name='listar_usuarios'),
    path('editar_usuario/<int:usuario_id>/', views.Editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:usuario_id>/', views.Eliminar_usuario, name='eliminar_usuario'),
]
