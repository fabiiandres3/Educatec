from django.shortcuts import render
from .selectors import obtener_alumnos_asistencia

###################  DASHBOARD DOCENTE  ######################

#@decorators.rol_requerido("docentes")
def dashboard_docente(request):
    return render(request, "paneles/docentes/dashboard_docente.html")


def cursos_docente(request):
    return render(request, "paneles/docentes/cursos_profesor.html")


def calificaciones_docente(request):

    return render(request, "paneles/docentes/calificaciones_docente.html")


def asistencia_docente(request):
    return render(
        request,
        'paneles/docentes/asistencia_docente.html'
    )


def historial_asistencia(request):
    return render(request, "paneles/docentes/historial_asistencia.html")


def guardar_asistencia(request):
    return render(request, "paneles/docentes"
    "/guardar_asistencia.html")


def configuracion_docente(request):
    return render(request, "paneles/docentes/configuracion_docente.html")


# ─────────────────────────────────────────
# ESTUDIANTE
# ─────────────────────────────────────────


def dashboard_estudiante(request):
    return render(request, "paneles/estudiante/dashboard_estudiante.html")


def materias_estudiante(request):
    return render(request, "paneles/estudiante/materias_estudiante.html")


def calificaciones_estudiante(request):
    return render(request, "paneles/estudiante/calificaciones_estudiante.html")


def asistencia_estudiante(request):
    alumnos = obtener_alumnos_asistencia()

    return render(request, "paneles/estudiante/asistencia_estudiante.html", 
                  
        {
            'alumnos': alumnos
        })


def logros_estudiante(request):
    return render(request, "paneles/estudiante/logros_estudiante.html")


def configuracion_estudiante(request):
    return render(request, "paneles/estudiante/configuracion_estudiante.html")
