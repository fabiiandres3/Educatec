# apps/paneles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    ###################  DASHBOARD DOCENTE  ######################
    path('dashboard_docente/', views.dashboard_docente, name='dashboard_docente'),
    path('docente_cursos/',         views.cursos_docente,         name='cursos_docente'),
    path('docente_calificaciones/', views.calificaciones_docente, name='calificacion_docente'),
    path('docente_asistencia/',     views.asistencia_docente,     name='asistencia_docente'),
    path('docente_asistencia/historial/', views.historial_asistencia, name='historial_asistencia'),
    path('docente_asistencia/guardar/',views.guardar_asistencia,name='guardar_asistencia'),
    path('docente_configuracion/',  views.configuracion_docente,  name='configuracion_docente'),

    # Estudiante
    path('dashboard_docente/',                views.dashboard_estudiante,    name='dashboard_alumno'),
    path('dashboard_docente/materias/',       views.materias_estudiante,     name='materias_alumno'),
    path('dashboard_docente/calificaciones/', views.calificaciones_estudiante, name='calificaciones_alumno'),
    path('dashboard_docente/asistencia/',     views.asistencia_estudiante,   name='asistencia_alumno'),
    path('dashboard_docente/logros/',         views.logros_estudiante,       name='logros_alumno'),
    path('dashboard_docente/configuracion/',  views.configuracion_estudiante, name='configuracion_alumno'),
]