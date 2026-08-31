import json
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from datetime import date, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.asistencia.models import Asistencia
from apps.cursos.models import Cursos
from apps.docentes.models import Docente, AsignacionDocente, MAX_CURSOS_POR_DOCENTE
from apps.eventos.models import Evento
from apps.tareas.models import Calificacion
from apps.alumnos.models import Acudiente, AcudienteAlumno, Alumnos

from .selectors import (
    obtener_tareas_docente,
    contar_alumnos_curso,
    obtener_alumnos_asistencia,
    obtener_cursos,
    obtener_materias,
    obtener_alumnos_por_curso,
    obtener_asistencia_por_curso_fecha,
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
    # ASIGNACIONES DEL DOCENTE
    # --------------------------------------------------------

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "clase",
        "clase__curso"
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
    # TOTAL DE ALUMNOS (suma de todos los cursos asignados)
    # --------------------------------------------------------

    cursos_ids = set()

    for asignacion in asignaciones:
        if asignacion.clase and asignacion.clase.curso:
            cursos_ids.add(asignacion.clase.curso.id)

    total_alumnoss = 0

    for curso_id in cursos_ids:
        total_alumnoss += contar_alumnos_curso(curso_id)

    # --------------------------------------------------------
    # TAREAS RECIENTES (de todas las asignaciones)
    # --------------------------------------------------------

    tareas_recientes = []

    for asignacion in asignaciones:

        if asignacion.clase and asignacion.clase.curso:

            tareas_recientes += list(
                obtener_tareas_docente(
                    asignacion.clase.id,
                    asignacion.clase.curso.id
                )
            )

    tareas_recientes = tareas_recientes[:5]

    total_tareas = len(tareas_recientes)

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
            "asignaciones": asignaciones,
            "eventos": eventos,
            "total_alumnoss": total_alumnoss,
            "total_tareas": total_tareas,
            "tareas_recientes": tareas_recientes,
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

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "clase",
        "clase__curso"
    )

    total_alumnos = 0

    for asignacion in asignaciones:

        if asignacion.clase and asignacion.clase.curso:

            asignacion.total_alumno = contar_alumnos_curso(
                asignacion.clase.curso.id
            )

            total_alumnos += asignacion.total_alumno

        else:

            asignacion.total_alumno = 0

    return render(
        request,
        "paneles/docentes/cursos_docente.html",
        {
            "docente": docente,
            "asignaciones": asignaciones,
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

    # --------------------------------------------------------
    # ASIGNACIONES DEL DOCENTE
    # --------------------------------------------------------

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "clase",
        "clase__curso"
    )

    # --------------------------------------------------------
    # ASIGNACIÓN SELECCIONADA
    # --------------------------------------------------------

    asignacion_id = request.GET.get("asignacion")

    asignacion_sel = None

    if asignacion_id:

        asignacion_sel = asignaciones.filter(
            id=asignacion_id
        ).first()

    if not asignacion_sel:

        asignacion_sel = asignaciones.first()

    curso_actual = (
        asignacion_sel.clase.curso
        if asignacion_sel
        else None
    )

    clase_actual = (
        asignacion_sel.clase
        if asignacion_sel
        else None
    )

    alumnos = []
    tareas = []

    # --------------------------------------------------------
    # TAREAS DEL DOCENTE
    # --------------------------------------------------------

    if curso_actual and clase_actual:

        tareas = list(
            obtener_tareas_docente(
                clase_actual.id,
                curso_actual.id
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
            curso_actual.id
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
            "asignaciones": asignaciones,
            "asignacion_sel": asignacion_sel,
            "curso_actual": curso_actual,
            "clase_actual": clase_actual,
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

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "clase",
        "clase__curso"
    )

    cursos_dict = {}

    for asignacion in asignaciones:

        if asignacion.clase and asignacion.clase.curso:

            curso = asignacion.clase.curso

            cursos_dict[curso.id] = curso

    cursos_docente = list(cursos_dict.values())

    curso_id = request.GET.get("curso")

    curso_sel = None

    if curso_id:

        try:
            curso_sel = cursos_dict.get(int(curso_id))
        except (ValueError, TypeError):
            curso_sel = None

    if not curso_sel and cursos_docente:
        curso_sel = cursos_docente[0]

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

    alumnos = []

    total = 0
    presentes = 0
    tardanzas = 0
    ausentes = 0

    if curso_sel:

        alumnos_qs = obtener_alumnos_por_curso(
            curso_sel.id
        )

        registros = obtener_asistencia_por_curso_fecha(
            curso_sel.id,
            fecha_sel
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

        total = len(alumnos)

        presentes = sum(
            1 for alumno in alumnos
            if alumno.estado_asistencia == "P"
        )

        tardanzas = sum(
            1 for alumno in alumnos
            if alumno.estado_asistencia == "T"
        )

        ausentes = sum(
            1 for alumno in alumnos
            if alumno.estado_asistencia == "A"
        )

    return render(
        request,
        "paneles/docentes/asistencia_docente.html",
        {
            "docente": docente,
            "cursos_docente": cursos_docente,
            "hoy": hoy,
            "fecha_hoy": hoy,
            "fecha_sel": fecha_sel,
            "alumnos": alumnos,
            "curso_sel": curso_sel,
            "total": total,
            "presentes": presentes,
            "tardanzas": tardanzas,
            "ausentes": ausentes,
        }
    )

def obtener_datos_asistencia(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Método no permitido"},
            status=405
        )

    curso_id = request.GET.get("curso")
    fecha_str = request.GET.get("fecha")

    if not curso_id or not fecha_str:

        return JsonResponse(
            {"error": "Curso y fecha son obligatorios"},
            status=400
        )

    try:
        curso_id = int(curso_id)

        fecha = datetime.strptime(
            fecha_str,
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):

        return JsonResponse(
            {"error": "Datos inválidos"},
            status=400
        )

    curso = get_object_or_404(
        Cursos,
        id=curso_id
    )

    alumnos = obtener_alumnos_por_curso(
        curso_id
    )

    asistencias = Asistencia.objects.filter(
        curso=curso,
        fecha=fecha
    )

    estado_map = {
        asistencia.alumno_id: asistencia.estado
        for asistencia in asistencias
    }

    data = []

    presentes = 0
    tardanzas = 0
    ausentes = 0

    for alumno in alumnos:

        estado = estado_map.get(
            alumno.id
        )

        if estado == "P":
            presentes += 1

        elif estado == "T":
            tardanzas += 1

        elif estado == "A":
            ausentes += 1

        data.append({
            "id": alumno.id,
            "nombre": alumno.usuario.get_full_name(),
            "codigo": alumno.codigo or "",
            "estado": estado,
        })

    return JsonResponse({
        "curso": {
            "id": curso.id,
            "nombre": curso.nombre,
        },
        "fecha": fecha.strftime("%Y-%m-%d"),
        "alumnos": data,
        "estadisticas": {
            "total": len(data),
            "presentes": presentes,
            "tardanzas": tardanzas,
            "ausentes": ausentes,
        }
    })


def guardar_asistencia_ajax(request):

    if request.method != "POST":

        return JsonResponse(
            {"error": "Método no permitido"},
            status=405
        )

    try:

        data = json.loads(
            request.body
        )

        curso_id = data.get("curso_id")
        fecha_str = data.get("fecha")
        asistencias = data.get("asistencias", [])

        if not curso_id or not fecha_str:

            return JsonResponse(
                {
                    "error": "Curso y fecha son obligatorios"
                },
                status=400
            )

        fecha = datetime.strptime(
            fecha_str,
            "%Y-%m-%d"
        ).date()

        curso = get_object_or_404(
            Cursos,
            id=curso_id
        )

        alumno_ids = [
            item.get("alumno_id")
            for item in asistencias
        ]

        alumnos_validos = set(
            Alumnos.objects.filter(
                id__in=alumno_ids,
                curso=curso,
                activo=True
            ).values_list(
                "id",
                flat=True
            )
        )

        with transaction.atomic():

            for item in asistencias:

                alumno_id = item.get(
                    "alumno_id"
                )

                estado = item.get(
                    "estado"
                )

                if alumno_id not in alumnos_validos:
                    continue

                if estado not in ["P", "T", "A"]:
                    continue

                Asistencia.objects.update_or_create(

                    alumno_id=alumno_id,

                    fecha=fecha,

                    defaults={
                        "curso": curso,
                        "estado": estado,
                    }
                )

        return JsonResponse({
            "success": True,
            "message": "Asistencia guardada correctamente"
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {"error": "JSON inválido"},
            status=400
        )

    except ValueError:

        return JsonResponse(
            {"error": "Fecha inválida"},
            status=400
        )

    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
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

    docente = Docente.objects.select_related(
        "usuario",
        "curso",
        "clase"
    ).get(
        usuario=request.user
    )

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "clase",
        "clase__curso"
    )

    if request.method == "POST":

        usuario = docente.usuario

        nombre_completo = request.POST.get("nombre", "").strip()
        correo = request.POST.get("correo", "").strip()
        telefono = request.POST.get("telefono", "").strip()

        partes = nombre_completo.split(" ", 1)
        usuario.first_name = partes[0] if partes else ""
        usuario.last_name = partes[1] if len(partes) > 1 else ""

        if correo:
            usuario.email = correo

        usuario.save()

        if telefono:

            try:
                docente.telefono = int(telefono)
                docente.save()
            except ValueError:
                messages.error(request, "El teléfono debe contener solo números.")
        else:
            docente.telefono = None
            docente.save()

        messages.success(request, "Perfil actualizado correctamente.")

        return redirect("configuracion_docente")

    return render(
        request,
        "paneles/docentes/configuracion_docente.html",
        {
            "docente": docente,
            "asignaciones": asignaciones,
        }
    )
    
# ============================================================
#                    CARGA ACADÉMICA
# ============================================================

def carga_academica(request):

    docentes = Docente.objects.select_related("usuario").all()

    filas = []

    for docente in docentes:

        asignaciones = AsignacionDocente.objects.filter(
            docente=docente
        ).select_related(
            "clase",
            "clase__curso"
        )

        filas.append(
            {
                "docente": docente,
                "asignaciones": asignaciones,
                "total": asignaciones.count(),
                "max": MAX_CURSOS_POR_DOCENTE,
            }
        )

    return render(
        request,
        "paneles/docentes/carga_academica.html",
        {
            "filas": filas,
        }
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



# ============================================================
#                    DASHBOARD ACUDIENTE
# ============================================================

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.alumnos.models import (
    Acudiente,
    AcudienteAlumno,
    Alumnos,
)

from apps.tareas.models import Calificacion
from apps.asistencia.models import Asistencia


# ============================================================
#                    PANEL ACUDIENTE
# ============================================================

def dashboard_acudiente(request):

    acudiente = get_object_or_404(
        Acudiente.objects.select_related("usuario"),
        usuario=request.user,
        activo=True
    )

    relaciones = (
        AcudienteAlumno.objects
        .filter(
            acudiente=acudiente,
            autorizado=True,
            alumno__activo=True
        )
        .select_related(
            "alumno",
            "alumno__usuario",
            "alumno__curso",
            "alumno__clase",
        )
        .order_by(
            "alumno__usuario__first_name",
            "alumno__usuario__last_name"
        )
    )

    alumnos = []

    for relacion in relaciones:

        alumno = relacion.alumno

        # -------------------------------------------------
        # CALIFICACIONES
        # -------------------------------------------------

        calificaciones = (
            Calificacion.objects
            .filter(
                alumno=alumno.usuario
            )
            .select_related("tarea")
            .order_by("-id")
        )

        notas = [
            float(cal.nota)
            for cal in calificaciones
            if cal.nota is not None
        ]

        promedio = (
            round(
                sum(notas) / len(notas),
                2
            )
            if notas
            else None
        )

        # -------------------------------------------------
        # ASISTENCIA
        # -------------------------------------------------

        asistencias = Asistencia.objects.filter(
            alumno=alumno
        )

        total_asistencias = asistencias.count()

        presentes = asistencias.filter(
            estado="P"
        ).count()

        porcentaje_asistencia = (

            round(
                (presentes / total_asistencias) * 100,
                1
            )

            if total_asistencias > 0

            else None
        )

        # -------------------------------------------------
        # TAREAS
        # -------------------------------------------------

        tareas_pendientes = 0

        if alumno.curso:

            tareas_pendientes = alumno.curso.tareas_set.count()

        # -------------------------------------------------
        # DATOS PARA LA PLANTILLA
        # -------------------------------------------------

        alumno.promedio = promedio

        alumno.porcentaje_asistencia = (
            porcentaje_asistencia
        )

        alumno.tareas_pendientes = (
            tareas_pendientes
        )

        alumno.parentesco = (
            relacion.parentesco
        )

        alumnos.append(alumno)

    return render(
        request,
        "paneles/acudientes/dashboard_acudiente.html",
        {
            "acudiente": acudiente,
            "alumnos": alumnos,
        }
    )


# ============================================================
#                    DETALLE DEL ALUMNO
# ============================================================

def detalle_alumno_acudiente(
    request,
    alumno_id
):

    acudiente = get_object_or_404(
        Acudiente,
        usuario=request.user,
        activo=True
    )

    relacion = get_object_or_404(
        AcudienteAlumno.objects.select_related(
            "alumno",
            "alumno__usuario",
            "alumno__curso",
            "alumno__clase",
        ),
        acudiente=acudiente,
        alumno_id=alumno_id,
        autorizado=True
    )

    alumno = relacion.alumno

    # -------------------------------------------------
    # CALIFICACIONES
    # -------------------------------------------------

    calificaciones = (
        Calificacion.objects
        .filter(
            alumno=alumno.usuario
        )
        .select_related(
            "tarea",
            "tarea__curso",
            "tarea__clase",
        )
        .order_by("-id")
    )

    notas = [
        float(cal.nota)
        for cal in calificaciones
        if cal.nota is not None
    ]

    promedio = (
        round(
            sum(notas) / len(notas),
            2
        )
        if notas
        else None
    )

    # -------------------------------------------------
    # ASISTENCIA
    # -------------------------------------------------

    asistencias = (
        Asistencia.objects
        .filter(
            alumno=alumno
        )
        .select_related("curso")
        .order_by("-fecha")
    )

    total = asistencias.count()

    presentes = asistencias.filter(
        estado="P"
    ).count()

    tardanzas = asistencias.filter(
        estado="T"
    ).count()

    ausentes = asistencias.filter(
        estado="A"
    ).count()

    porcentaje_asistencia = (

        round(
            (presentes / total) * 100,
            1
        )

        if total > 0

        else None
    )

    return render(
        request,
        "paneles/acudientes/detalle_alumno.html",
        {
           
        }
    )