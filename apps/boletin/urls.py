from django.urls import path

from . import views


urlpatterns = [
    path("docente/boletines/", views.boletines_docente, name="boletines_docente"),
    path("docente/boletines/<int:asignacion_id>/<int:alumno_id>/<int:periodo_id>/", views.editar_boletin_docente, name="editar_boletin_docente"),
    path("alumno/boletines/", views.mis_boletines, name="mis_boletines"),
    path("administrador/boletines/", views.boletines_administrador, name="boletines_administrador"),
    path("administrador/boletines/<int:alumno_id>/<int:periodo_id>/", views.ver_boletin_administrador, name="ver_boletin_administrador"),
    path("boletines/<int:alumno_id>/<int:periodo_id>/pdf/", views.descargar_boletin_pdf, name="descargar_boletin_pdf"),
]
