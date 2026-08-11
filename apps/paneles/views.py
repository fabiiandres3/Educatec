from datetime import date, datetime

from django.shortcuts import render

from apps.asistencia.models import Asistencia
from apps.docentes.models import Docente
from apps.eventos.models import Evento
from apps.tareas.models import Calificacion

from .selectors import (
    obtener_tareas_docente,
    contar_alumnos_curso,
    obtener_alumnos_asistencia,
    obtener_cursos,
    obtener_materias,
    obtener_alumnos_por_curso,
)


# ============================================================
#                    DASHBOARD DOCENTE
# ============================================================

def dashboard_docente(request):

    # --------------------------------------------------------
    # DOCENTE ACTUAL
    # --------------------------------------------------------

    docente = Docente.objects.select_related(
        "curso",
        "clase"
    ).get(
        usuario=request.user
    )

    # --------------------------------------------------------
    # EVENTOS PARA DOCENTES
    # --------------------------------------------------------

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "docentes"]
    ).order_by(
        "fecha",
        "hora"
    )

    # --------------------------------------------------------
    # CURSOS
    # --------------------------------------------------------

    cursos = obtener_cursos()

    # --------------------------------------------------------
    # TOTAL DE ALUMNOS
    # --------------------------------------------------------

    total_alumnoss = 0

    if docente.curso:
        total_alumnoss = contar_alumnos_curso(
            docente.curso.id
        )

    # --------------------------------------------------------
    # TAREAS RECIENTES
    # --------------------------------------------------------

    tareas_recientes = []

    if docente.curso and docente.clase:

        tareas_recientes = list(
            obtener_tareas_docente(
                docente.clase.id,
                docente.curso.id
            )
        )[:5]

    total_tareas = len(tareas_recientes)

    # --------------------------------------------------------
    # MATERIAS
    # --------------------------------------------------------

    materias = obtener_materias()

    # --------------------------------------------------------
    # ESTADÍSTICAS
    # --------------------------------------------------------

    porcentaje_asistencia = "—"
    promedio = "—"

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "paneles/docentes/dashboard_docente.html",
        {
            "docente": docente,
            "eventos": eventos,
            "cursos": cursos,
            "total_alumnoss": total_alumnoss,
            "total_tareas": total_tareas,
            "tareas_recientes": tareas_recientes,
            "materias": materias,
            "porcentaje_asistencia": porcentaje_asistencia,
            "promedio": promedio,
        }
    )


# ============================================================
#                    EVENTOS DOCENTE
# ============================================================

def eventos_docente(request):

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "docentes"]
    ).order_by(
        "fecha",
        "hora"
    )

    return render(
        request,
        "admin/eventos/eventos_docente.html",
        {
            "eventos": eventos,
        }
    )


# ============================================================
#                    CURSOS DOCENTE
# ============================================================

def cursos_docente(request):

    docente = Docente.objects.select_related(
        "curso",
        "clase"
    ).get(
        usuario=request.user
    )

    total_alumnos = 0

    if docente.curso:
        total_alumnos = contar_alumnos_curso(
            docente.curso.id
        )

    return render(
        request,
        "paneles/docentes/cursos_docente.html",
        {
            "docente": docente,
            "total_alumnos": total_alumnos,
        }
    )


# ============================================================
#                    CALIFICACIONES DOCENTE
# ============================================================

def calificaciones_docente(request):

    docente = Docente.objects.select_related(
        "curso",
        "clase"
    ).get(
        usuario=request.user
    )

    alumnos = []
    tareas = []

    # --------------------------------------------------------
    # TAREAS DEL DOCENTE
    # --------------------------------------------------------

    if docente.curso and docente.clase:

        tareas = list(
            obtener_tareas_docente(
                docente.clase.id,
                docente.curso.id
            )
        )

        tarea_ids = [
            tarea.id
            for tarea in tareas
        ]

        # ----------------------------------------------------
        # CALIFICACIONES
        # ----------------------------------------------------

        calificaciones = Calificacion.objects.filter(
            tarea_id__in=tarea_ids
        )

        notas_map = {
            (calificacion.alumno_id, calificacion.tarea_id):
            calificacion.nota
            for calificacion in calificaciones
        }

        # ----------------------------------------------------
        # ALUMNOS
        # ----------------------------------------------------

        alumnos_qs = obtener_alumnos_por_curso(
            docente.curso.id
        )

        for alumno in alumnos_qs:

            fila_notas = []
            valores = []

            for tarea in tareas:

                nota = notas_map.get(
                    (
                        alumno.usuario_id,
                        tarea.id
                    )
                )

                fila_notas.append(
                    {
                        "tarea_id": tarea.id,
                        "nota": nota,
                    }
                )

                if nota is not None:
                    valores.append(
                        float(nota)
                    )

            alumno.fila_notas = fila_notas

            alumno.promedio = (
                round(
                    sum(valores) / len(valores),
                    2
                )
                if valores
                else None
            )

            alumnos.append(alumno)

    # --------------------------------------------------------
    # ESTADÍSTICAS
    # --------------------------------------------------------

    promedios = [
        alumno.promedio
        for alumno in alumnos
        if alumno.promedio is not None
    ]

    promedio_general = (
        round(
            sum(promedios) / len(promedios),
            2
        )
        if promedios
        else "—"
    )

    en_riesgo = len(
        [
            promedio
            for promedio in promedios
            if promedio < 3.0
        ]
    )

    destacados = len(
        [
            promedio
            for promedio in promedios
            if promedio >= 4.5
        ]
    )

    total_notas = sum(
        1
        for alumno in alumnos
        for fila in alumno.fila_notas
        if fila["nota"] is not None
    )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

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
        }
    )


# ============================================================
#                    ASISTENCIA DOCENTE
# ============================================================

def asistencia_docente(request):

    docente = Docente.objects.select_related(
        "curso",
        "clase"
    ).get(
        usuario=request.user
    )

    hoy = date.today()

    # --------------------------------------------------------
    # FECHA SELECCIONADA
    # --------------------------------------------------------

    fecha_str = request.GET.get("fecha")

    if fecha_str:

        try:

            fecha_sel = datetime.strptime(
                fecha_str,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            fecha_sel = hoy

    else:

        fecha_sel = hoy

    # --------------------------------------------------------
    # VARIABLES
    # --------------------------------------------------------

    alumnos = []

    total = 0
    presentes = 0
    tardanzas = 0
    ausentes = 0

    # --------------------------------------------------------
    # ALUMNOS DEL CURSO
    # --------------------------------------------------------

    if docente.curso:

        alumnos_qs = obtener_alumnos_por_curso(
            docente.curso.id
        )

        registros = Asistencia.objects.filter(
            curso=docente.curso,
            fecha=fecha_sel
        )

        estado_map = {
            registro.alumno_id: registro.estado
            for registro in registros
        }

        for alumno in alumnos_qs:

            alumno.estado_asistencia = estado_map.get(
                alumno.id
            )

            alumnos.append(alumno)

        # ----------------------------------------------------
        # ESTADÍSTICAS
        # ----------------------------------------------------

        total = len(alumnos)

        presentes = sum(
            1
            for alumno in alumnos
            if alumno.estado_asistencia == "P"
        )

        tardanzas = sum(
            1
            for alumno in alumnos
            if alumno.estado_asistencia == "T"
        )

        ausentes = sum(
            1
            for alumno in alumnos
            if alumno.estado_asistencia == "A"
        )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

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
        }
    )


# ============================================================
#                    HISTORIAL ASISTENCIA
# ============================================================

def historial_asistencia(request):

    return render(
        request,
        "paneles/docentes/historial_asistencia.html"
    )


# ============================================================
#                    GUARDAR ASISTENCIA
# ============================================================

def guardar_asistencia(request):

    return render(
        request,
        "paneles/docentes/guardar_asistencia.html"
    )


# ============================================================
#                    CONFIGURACIÓN DOCENTE
# ============================================================

def configuracion_docente(request):

    return render(
        request,
        "paneles/docentes/configuracion_docente.html"
    )


# ============================================================
#                    DASHBOARD ALUMNOS
# ============================================================

def dashboard_alumnos(request):

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "alumnos"]
    ).order_by(
        "fecha",
        "hora"
    )

    return render(
        request,
        "paneles/alumnos/dashboard_alumnos.html",
        {
            "eventos": eventos,
        }
    )


# ============================================================
#                    MATERIAS ALUMNOS
# ============================================================

def materias_alumnos(request):

    return render(
        request,
        "paneles/alumnos/materias_alumnos.html"
    )


# ============================================================
#                    CALIFICACIONES ALUMNOS
# ============================================================

def calificaciones_alumnos(request):

    return render(
        request,
        "paneles/alumnos/calificaciones_alumnos.html"
    )


# ============================================================
#                    ASISTENCIA ALUMNOS
# ============================================================

def asistencia_alumnos(request):

    alumnos = obtener_alumnos_asistencia()

    return render(
        request,
        "paneles/alumnos/asistencia_alumnos.html",
        {
            "alumnos": alumnos,
        }
    )


# ============================================================
#                    LOGROS ALUMNOS
# ============================================================

def logros_alumnos(request):

    return render(
        request,
        "paneles/alumnos/logros_alumnos.html"
    )


# ============================================================
#                    CONFIGURACIÓN ALUMNOS
# ============================================================

def configuracion_alumnos(request):

    return render(
        request,
        "paneles/alumnos/configuracion_alumnos.html"
    )
