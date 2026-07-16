# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.user.urls')),
    path('paneles/', include('apps.paneles.urls')),
    path('', include('apps.clases.urls')),
    path('', include('apps.tareas.urls')),
    path('', include('apps.cursos.urls')),
    path('', include('apps.administrador.urls')),
]

