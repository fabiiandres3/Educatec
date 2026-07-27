from django.shortcuts import render
from .selectors import obtener_alumnos_asistencia

###################  DASHBOARD DOCENTE  ######################

#@decorators.rol_requerido("docentes")
def dashboard_docente(request):
    return render(request, "paneles/docentes/dashboard_docente.html")


def cursos_docente(request):
    return render(request, "paneles/docentes/cursos_docente.html")


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
# alumnos
# ─────────────────────────────────────────


def dashboard_alumnos(request):
    return render(request, "paneles/alumnos/dashboard_alumnos.html")


def materias_alumnos(request):
    return render(request, "paneles/alumnos/materias_alumnos.html")


def calificaciones_alumnos(request):
    return render(request, "paneles/alumnos/calificaciones_alumnos.html")


def asistencia_alumnos(request):
    alumnos = obtener_alumnos_asistencia()

    return render(request, "paneles/alumnos/asistencia_alumnos.html", 
                  
        {
            'alumnos': alumnos
        })


def logros_alumnos(request):
    return render(request, "paneles/alumnos/logros_alumnos.html")


def configuracion_alumnos(request):
    return render(request, "paneles/alumnos/configuracion_alumnos.html")
