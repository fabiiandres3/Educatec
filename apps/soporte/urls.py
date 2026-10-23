from django.urls import path

from apps.soporte import views


urlpatterns = [
    path("soporte/solicitud/", views.solicitud_soporte, name="solicitud_soporte"),
    path(
        "admin/notificaciones-correo/",
        views.notificaciones_correo_admin,
        name="notificaciones_correo_admin",
    ),
]
