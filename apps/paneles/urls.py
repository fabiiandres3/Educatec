# apps/paneles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    ###################  DASHBOARD DOCENTE  ######################
    path('dashboard_docente/', views.dashboard_docente, name='dashboard_docente'),
    #path('profesor/cursos/',         views.cursos_profesor,         name='cursos_profesor'),
    #path('profesor/calificaciones/', views.calificaciones_profesor, name='calificaciones_profesor'),
    #path('profesor/asistencia/',     views.asistencia_profesor,     name='asistencia_profesor'),
    #path('profesor/asistencia/historial/', views.historial_asistencia, name='historial_asistencia'),
    #path('profesor/asistencia/guardar/',views.guardar_asistencia,name='guardar_asistencia'),
    #path('profesor/configuracion/',  views.configuracion_profesor,  name='configuracion_profesor'),

    # Estudiante
    #path('estudiante/',                views.dashboard_estudiante,    name='dashboard_estudiante'),
    #path('estudiante/materias/',       views.materias_estudiante,     name='materias_estudiante'),
    #path('estudiante/calificaciones/', views.calificaciones_estudiante, name='calificaciones_estudiante'),
    #path('estudiante/asistencia/',     views.asistencia_estudiante,   name='asistencia_estudiante'),
    #path('estudiante/logros/',         views.logros_estudiante,       name='logros_estudiante'),
    #path('estudiante/configuracion/',  views.configuracion_estudiante, name='configuracion_estudiante'),
]