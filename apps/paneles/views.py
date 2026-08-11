from django.shortcuts import render
from datetime import date, datetime
from apps.cursos.models import Cursos
from apps.docentes.models import Docente
from apps.tareas.models import Calificacion
from apps.asistencia.models import Asistencia
from .selectors import (obtener_tareas_docente, contar_alumnos_curso, obtener_curso, obtener_docente, obtener_alumnos_asistencia,obtener_cursos,contar_alumnos,contar_materias,contar_alumnos_curso, obtener_materias,obtener_alumnos_por_curso)

###################  DASHBOARD DOCENTE  ######################

#@decorators.rol_requerido("docentes")
def dashboard_docente(request):
    return render(request, "paneles/docentes/dashboard_docente.html")


def cursos_docente(request):
    docente = Docente.objects.select_related("curso", "clase").get(usuario=request.user)

    total_alumnos = 0
    if docente.curso:
        total_alumnos = contar_alumnos_curso(docente.curso.id)

    return render(request, "paneles/docentes/cursos_docente.html", {
        "docente": docente,
        "total_alumnos": total_alumnos,
    })


def calificaciones_docente(request):
    docente = Docente.objects.select_related("curso", "clase").get(usuario=request.user)

    alumnos = []
    tareas = []

    if docente.curso and docente.clase:
        tareas = list(obtener_tareas_docente(docente.clase.id, docente.curso.id))
        tarea_ids = [t.id for t in tareas]

        calificaciones = Calificacion.objects.filter(tarea_id__in=tarea_ids)
        notas_map = {(c.alumno_id, c.tarea_id): c.nota for c in calificaciones}

        alumnos_qs = obtener_alumnos_por_curso(docente.curso.id)
        for alumno in alumnos_qs:
            fila_notas = []
            valores = []
            for t in tareas:
                nota = notas_map.get((alumno.usuario_id, t.id))
                fila_notas.append({"tarea_id": t.id, "nota": nota})
                if nota is not None:
                    valores.append(float(nota))
            alumno.fila_notas = fila_notas
            alumno.promedio = round(sum(valores) / len(valores), 2) if valores else None
            alumnos.append(alumno)

    promedios = [a.promedio for a in alumnos if a.promedio is not None]
    promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else "—"
    en_riesgo = len([p for p in promedios if p < 3.0])
    destacados = len([p for p in promedios if p >= 4.5])
    total_notas = sum(1 for a in alumnos for f in a.fila_notas if f["nota"] is not None)

    return render(
        request,
        "paneles/docentes/calificaciones_docente.html",
        {
            "docente": docente,
            "alumnos": alumnos,
            "tareas": tareas,
            "total_notas": total_notas,
            "promedio_general": promedio_general,
            "en_riesgo": en_riesgo,
            "destacados": destacados,
        },
    )


def asistencia_docente(request):
    docente = Docente.objects.select_related("curso", "clase").get(usuario=request.user)
    hoy = date.today()

    fecha_str = request.GET.get("fecha")
    if fecha_str:
        try:
            fecha_sel = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_sel = hoy
    else:
        fecha_sel = hoy

    alumnos = []
    total = presentes = tardanzas = ausentes = 0

    if docente.curso:
        alumnos_qs = obtener_alumnos_por_curso(docente.curso.id)
        registros = Asistencia.objects.filter(curso=docente.curso, fecha=fecha_sel)
        estado_map = {r.alumno_id: r.estado for r in registros}

        for alumno in alumnos_qs:
            alumno.estado_asistencia = estado_map.get(alumno.id)
            alumnos.append(alumno)

        total = len(alumnos)
        presentes = sum(1 for a in alumnos if a.estado_asistencia == "P")
        tardanzas = sum(1 for a in alumnos if a.estado_asistencia == "T")
        ausentes = sum(1 for a in alumnos if a.estado_asistencia == "A")

    return render(
        request,
        "paneles/docentes/asistencia_docente.html",
        {
            "docente": docente,
            "hoy": hoy,
            "fecha_hoy": hoy,
            "fecha_sel": fecha_sel,
            "alumnos": alumnos,
            "curso_sel": docente.curso,
            "total": total,
            "presentes": presentes,
            "tardanzas": tardanzas,
            "ausentes": ausentes,
        },
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
