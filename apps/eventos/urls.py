from django.urls import path

from . import views


urlpatterns = [
    path("", views.listar_eventos, name="listar_eventos"),

    path(
        "crear/",
        views.crear_evento,
        name="crear_evento"
    ),
]