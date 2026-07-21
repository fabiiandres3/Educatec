from django.urls import path
from apps.user import views

urlpatterns = [
    path('', views.index, name='index'),
    path('prescolar/', views.prescolar, name='prescolar'),
    path('primaria/', views.primaria, name='primaria'),
    path('secundaria/', views.secundaria, name='secundaria'),

    #LOGIN del proyecto
    path('registrar_usuario/', views.Registrar_usuario, name='registrar_usuario'),
    path('login/', views.iniciar_sesion, name='login'),
    path("cerrar/sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    path('verificacion/', views.verificacion, name='verificacion'),
    path('dashboard/', views.dashboard, name='dashboard_administrador'),


    #ADMINISTRADOR
    path('listar_usuarios/', views.Listar_usuarios, name='listar_usuarios'),
    path('editar_usuario/<int:usuario_id>/', views.Editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:usuario_id>/', views.Eliminar_usuario, name='eliminar_usuario'),
]