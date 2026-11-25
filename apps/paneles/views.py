import json
from collections import defaultdict
from datetime import date, datetime
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from apps.user.decorators import rol_requerido

from apps.clases.models import Clases
from apps.asistencia.models import Asistencia
from apps.cursos.models import Cursos
from apps.docentes.models import (
    Docente,
    AsignacionDocente,
    MAX_CURSOS_POR_DOCENTE,
)
from apps.eventos.models import Evento
from apps.tareas.models import (
    Tareas,
    Calificacion,
    ActividadCalificacion,
    CalificacionActividad,
)
from apps.calificaciones.services import (
    calcular_promedio_calificaciones,
    obtener_promedio_general_alumno,
    obtener_libro_calificaciones,
)
from apps.alumnos.models import (
    Acudiente,
    AcudienteAlumno,
    Alumnos,
)

from apps.horario.models import (
    Horario,
    Periodo,
)

from .selectors import (
    obtener_tareas_docente,
    contar_alumnos_curso,
    obtener_cursos,
    obtener_materias,
    obtener_alumnos_por_curso,
    obtener_asistencia_por_curso_fecha,
    obtener_resumen_tareas_por_alumno,
)
from .forms import CuentaPerfilForm


# ============================================================
#                    DASHBOARD DOCENTE
# ============================================================

@rol_requerido("docente")
def dashboard_docente(request):
    docente = Docente.objects.select_related("usuario").get(usuario=request.user)
    asignaciones = list(
        AsignacionDocente.objects.filter(docente=docente)
        .select_related("curso", "clase")
        .prefetch_related("clase__cursos")
    )

    cursos_unicos = {}
    asignaciones_calificaciones = []
    cursos_ids = set()
    for asignacion in asignaciones:
        if asignacion.curso_id:
            cursos_unicos.setdefault(asignacion.curso_id, asignacion.curso)
            asignaciones_calificaciones.append(asignacion)
            cursos_ids.add(asignacion.curso_id)
        elif asignacion.clase_id:
            for curso in asignacion.clase.cursos.all():
                cursos_unicos.setdefault(curso.id, curso)
                asignaciones_calificaciones.append(SimpleNamespace(
                    docente=docente,
                    curso=curso,
                    curso_id=curso.id,
                    clase=asignacion.clase,
                    clase_id=asignacion.clase_id,
                ))
                cursos_ids.add(curso.id)

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "docentes"],
        fecha__gte=timezone.localdate(),
    ).order_by("fecha", F("hora_inicio").asc(nulls_last=True), "pk")

    conteos_alumnos = Alumnos.objects.filter(
        curso_id__in=cursos_ids,
        activo=True,
    ).values("curso_id").annotate(total=Count("id"))
    total_alumnoss = sum(item["total"] for item in conteos_alumnos)

    tarea_ids = set()
    actividad_ids = set()
    for asignacion in asignaciones_calificaciones:
        _, tareas_asignacion, actividades_asignacion = obtener_libro_calificaciones(asignacion)
        tarea_ids.update(tarea.id for tarea in tareas_asignacion)
        actividad_ids.update(actividad.id for actividad in actividades_asignacion)

    tareas_query = Tareas.objects.filter(id__in=tarea_ids).select_related("curso", "clase")
    tareas_recientes = list(tareas_query.order_by("-fecha_creacion", "-id")[:5])
    registros_calificacion = list(
        Calificacion.objects.filter(tarea_id__in=tarea_ids, nota__isnull=False)
    ) + list(
        CalificacionActividad.objects.filter(
            actividad_id__in=actividad_ids,
            nota__isnull=False,
        )
    )
    promedio_calificaciones = calcular_promedio_calificaciones(registros_calificacion)
    promedio = float(promedio_calificaciones) if promedio_calificaciones is not None else "—"

    registros_asistencia = Asistencia.objects.filter(
        curso_id__in=cursos_ids,
    ).aggregate(
        total=Count("id"),
        asistieron=Count("id", filter=Q(estado__in=["P", "T"])),
    )
    total_registros = registros_asistencia["total"]
    porcentaje_asistencia = (
        round(registros_asistencia["asistieron"] / total_registros * 100, 1)
        if total_registros else "\u2014"
    )

    return render(
        request,
        "paneles/docentes/dashboard_docente.html",
        {
            "docente": docente,
            "asignaciones": asignaciones,
            "cursos_asignados": sorted(cursos_unicos.values(), key=lambda curso: curso.nombre.lower()),
            "eventos": eventos,
            "total_alumnoss": total_alumnoss,
            "total_tareas": tareas_query.count(),
            "porcentaje_asistencia": porcentaje_asistencia,
            "promedio": promedio,
            "tareas_recientes": tareas_recientes,
        },
    )

# ============================================================
#                    EVENTOS DOCENTE
# ============================================================

@rol_requerido("docente")
def eventos_docente(request):

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "docentes"]
    ).order_by(
        "fecha",
        "hora_inicio"
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


@rol_requerido("docente")
def cursos_docente(request):

    docente = Docente.objects.select_related(
        "usuario"
    ).get(
        usuario=request.user
    )

    asignaciones = list(
        AsignacionDocente.objects
        .filter(docente=docente)
        .filter(curso__isnull=False)
        .select_related("curso")
    )

    cursos_por_id = {}
    for asignacion in asignaciones:
        cursos_por_id.setdefault(asignacion.curso_id, (asignacion.curso, asignacion))

    cursos_asignados = []
    total_alumnos = 0
    for curso, asignacion in sorted(cursos_por_id.values(), key=lambda item: item[0].nombre.lower()):
        total_curso = contar_alumnos_curso(curso.id)
        total_alumnos += total_curso
        cursos_asignados.append(SimpleNamespace(
            id=asignacion.id,
            curso=curso,
            total_alumno=total_curso,
        ))

    return render(
        request,
        "paneles/docentes/cursos_docente.html",
        {
            "docente": docente,
            "asignaciones": cursos_asignados,
            "total_alumnos": total_alumnos,
        }
    )

# ============================================================
#                    CALIFICACIONES DOCENTE
# ============================================================

@rol_requerido("docente")
def calificaciones_docente(request):

    docente = Docente.objects.select_related(
        "usuario"
    ).get(
        usuario=request.user
    )

    # --------------------------------------------------------
    # ASIGNACIONES DEL DOCENTE
    # --------------------------------------------------------

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "docente",
        "curso"
    )

    # --------------------------------------------------------
    # ASIGNACIÓN SELECCIONADA
    # --------------------------------------------------------

    asignacion_id = request.GET.get(
        "asignacion"
    )

    asignacion_sel = None

    if asignacion_id:

        asignacion_sel = asignaciones.filter(
            id=asignacion_id
        ).first()

    if not asignacion_sel:

        asignacion_sel = asignaciones.first()

    curso_actual = (
        asignacion_sel.curso
        if asignacion_sel
        else None
    )

    # AsignacionDocente ya no tiene "clase".
    # Para obtener tareas se consultan las clases pertenecientes al curso.
    clases_actuales = (
        Clases.objects.filter(cursos=curso_actual)
        if curso_actual
        else Clases.objects.none()
    )

    clase_actual = (
        clases_actuales.first()
        if curso_actual
        else None
    )

    alumnos = []
    tareas = []

    # --------------------------------------------------------
    # TAREAS DEL DOCENTE
    # --------------------------------------------------------

    if curso_actual:

        for clase in clases_actuales:
            tareas.extend(
                obtener_tareas_docente(
                    clase.id,
                    curso_actual.id
                )
            )

        tareas = list(tareas)

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
            (
                calificacion.alumno_id,
                calificacion.tarea_id
            ): calificacion.nota

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

            alumnos.append(
                alumno
            )

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

@rol_requerido("docente")
def asistencia_docente(request):

    docente = Docente.objects.select_related(
        "usuario"
    ).get(
        usuario=request.user
    )

    hoy = timezone.localdate()

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "docente",
        "curso"
    )

    cursos_dict = {}

    for asignacion in asignaciones:

        if asignacion.curso:

            curso = asignacion.curso

            cursos_dict[curso.id] = curso

    cursos_docente = list(
        cursos_dict.values()
    )

    curso_id = request.GET.get(
        "curso"
    )

    curso_sel = None

    if curso_id:

        try:

            curso_sel = cursos_dict.get(
                int(curso_id)
            )

        except (
            ValueError,
            TypeError
        ):

            curso_sel = None

    if not curso_sel and cursos_docente:

        curso_sel = cursos_docente[0]

    fecha_str = request.GET.get(
        "fecha"
    )

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

    if fecha_sel > hoy:
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

            alumnos.append(
                alumno
            )

        total = len(
            alumnos
        )

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


# ============================================================
#                    DATOS ASISTENCIA AJAX
# ============================================================

@rol_requerido("docente")
def obtener_datos_asistencia(request):

    if request.method != "GET":

        return JsonResponse(
            {
                "error": "Método no permitido"
            },
            status=405
        )

    curso_id = request.GET.get(
        "curso"
    )

    fecha_str = request.GET.get(
        "fecha"
    )

    if not curso_id or not fecha_str:

        return JsonResponse(
            {
                "error": "Curso y fecha son obligatorios"
            },
            status=400
        )

    try:

        curso_id = int(
            curso_id
        )

        fecha = datetime.strptime(
            fecha_str,
            "%Y-%m-%d"
        ).date()

    except (
        ValueError,
        TypeError
    ):

        return JsonResponse(
            {
                "error": "Datos inválidos"
            },
            status=400
        )

    if fecha > timezone.localdate():
        return JsonResponse({"error": "No se puede consultar asistencia de una fecha futura."}, status=400)

    docente = get_object_or_404(Docente, usuario=request.user)
    if not AsignacionDocente.objects.filter(docente=docente, curso_id=curso_id).exists():
        return JsonResponse({"error": "No tienes acceso a este curso."}, status=403)

    curso = get_object_or_404(Cursos, id=curso_id)

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

        data.append(
            {
                "id": alumno.id,
                "nombre": alumno.usuario.get_full_name() or alumno.usuario.documento or "Alumno",
                "codigo": alumno.usuario.documento or "",
                "estado": estado,
            }
        )

    return JsonResponse(
        {
            "curso": {
                "id": curso.id,
                "nombre": curso.nombre,
            },
            "fecha": fecha.strftime(
                "%Y-%m-%d"
            ),
            "alumnos": data,
            "estadisticas": {
                "total": len(data),
                "presentes": presentes,
                "tardanzas": tardanzas,
                "ausentes": ausentes,
            }
        }
    )


# ============================================================
#                    GUARDAR ASISTENCIA AJAX
# ============================================================

@rol_requerido("docente")
def guardar_asistencia_ajax(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "Método no permitido"
            },
            status=405
        )

    try:

        data = json.loads(request.body)
        if not isinstance(data, dict):
            return JsonResponse({"error": "El contenido enviado no es válido."}, status=400)

        curso_id = data.get(
            "curso_id"
        )

        fecha_str = data.get(
            "fecha"
        )

        asistencias = data.get(
            "asistencias",
            []
        )

        if not curso_id or not fecha_str:

            return JsonResponse(
                {
                    "error": "Curso y fecha son obligatorios"
                },
                status=400
            )

        curso_id = int(curso_id)
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        if fecha > timezone.localdate():
            return JsonResponse({"error": "No se puede guardar asistencia en una fecha futura."}, status=400)

        if not isinstance(asistencias, list) or not asistencias:
            return JsonResponse({"error": "Selecciona al menos un estado de asistencia."}, status=400)

        docente = get_object_or_404(Docente, usuario=request.user)
        if not AsignacionDocente.objects.filter(docente=docente, curso_id=curso_id).exists():
            return JsonResponse({"error": "No tienes permiso para registrar asistencia en este curso."}, status=403)

        curso = get_object_or_404(
            Cursos,
            id=curso_id
        )

        alumno_ids = []
        estados_por_alumno = {}
        estados_validos = {estado for estado, _ in Asistencia.ESTADOS}
        for item in asistencias:
            if not isinstance(item, dict):
                return JsonResponse({"error": "Hay un registro de asistencia inválido."}, status=400)
            try:
                alumno_id = int(item.get("alumno_id"))
            except (TypeError, ValueError):
                return JsonResponse({"error": "Hay un alumno inválido en la solicitud."}, status=400)
            estado = item.get("estado")
            if estado not in estados_validos:
                return JsonResponse({"error": "Selecciona un estado válido para cada alumno."}, status=400)
            if alumno_id in estados_por_alumno:
                return JsonResponse({"error": "Hay alumnos repetidos en la solicitud."}, status=400)
            alumno_ids.append(alumno_id)
            estados_por_alumno[alumno_id] = estado

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

        if alumnos_validos != set(alumno_ids):
            return JsonResponse({"error": "Uno o más alumnos no pertenecen a este curso o están inactivos."}, status=400)

        with transaction.atomic():

            for alumno_id, estado in estados_por_alumno.items():
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
            "guardados": len(estados_por_alumno),
            "message": "Asistencia guardada correctamente",
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "JSON inválido"
            },
            status=400
        )

    except ValueError:

        return JsonResponse(
            {
                "error": "Fecha inválida"
            },
            status=400
        )

    except (TypeError, KeyError):
        return JsonResponse({"error": "Los datos enviados no son válidos."}, status=400)
    except Exception:
        return JsonResponse({"error": "No se pudo guardar la asistencia. Intenta nuevamente."}, status=500)


# ============================================================
#                    HISTORIAL ASISTENCIA
# ============================================================

@rol_requerido("docente")
def historial_asistencia(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    cursos = Cursos.objects.filter(
        asignaciones_docentes__docente=docente
    ).distinct().order_by("nombre")
    curso_sel = cursos.filter(pk=request.GET.get("curso")).first() if request.GET.get("curso") else cursos.first()
    hoy = timezone.localdate()
    try:
        fecha_sel = datetime.strptime(request.GET.get("fecha", ""), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        fecha_sel = hoy
    if fecha_sel > hoy:
        fecha_sel = hoy

    filas = []
    if curso_sel:
        alumnos = Alumnos.objects.filter(curso=curso_sel, activo=True).select_related("usuario").order_by(
            "usuario__last_name", "usuario__first_name"
        )
        registros = Asistencia.objects.filter(curso=curso_sel, fecha=fecha_sel)
        por_alumno = {registro.alumno_id: registro for registro in registros}
        filas = [{"alumnos": alumno, "asistencia": por_alumno.get(alumno.id)} for alumno in alumnos]

    return render(request, "paneles/docentes/historial_asistencia_registros.html", {
        "docente": docente,
        "cursos": cursos,
        "curso_sel": curso_sel,
        "fecha_sel": fecha_sel,
        "hoy": hoy,
        "filas": filas,
    })


# ============================================================
#                    GUARDAR ASISTENCIA
# ============================================================

@rol_requerido("docente")
def guardar_asistencia(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    alumno_id = request.POST.get("alumno_id") or request.POST.get("alumnos_id")
    fecha_str = request.POST.get("fecha")
    estado = request.POST.get("estado")
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        alumno_id = int(alumno_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Alumno o fecha inválidos."}, status=400)
    if fecha > timezone.localdate():
        return JsonResponse({"error": "No se puede guardar asistencia en una fecha futura."}, status=400)
    if estado not in {estado for estado, _ in Asistencia.ESTADOS}:
        return JsonResponse({"error": "Selecciona un estado válido."}, status=400)

    docente = get_object_or_404(Docente, usuario=request.user)
    alumno = get_object_or_404(Alumnos.objects.select_related("curso"), pk=alumno_id, activo=True)
    if not alumno.curso or not AsignacionDocente.objects.filter(docente=docente, curso=alumno.curso).exists():
        return JsonResponse({"error": "No tienes acceso a este alumno."}, status=403)
    Asistencia.objects.update_or_create(
        alumno=alumno, fecha=fecha,
        defaults={"curso": alumno.curso, "estado": estado},
    )
    return JsonResponse({"success": True, "message": "Asistencia actualizada."})


@rol_requerido("docente")
def eliminar_asistencia(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)
    alumno_id = request.POST.get("alumno_id") or request.POST.get("alumnos_id")
    fecha_str = request.POST.get("fecha")
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        alumno_id = int(alumno_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Alumno o fecha inválidos."}, status=400)
    if fecha > timezone.localdate():
        return JsonResponse({"error": "No se puede modificar una fecha futura."}, status=400)

    docente = get_object_or_404(Docente, usuario=request.user)
    alumno = get_object_or_404(Alumnos.objects.select_related("curso"), pk=alumno_id, activo=True)
    if not alumno.curso or not AsignacionDocente.objects.filter(docente=docente, curso=alumno.curso).exists():
        return JsonResponse({"error": "No tienes acceso a este alumno."}, status=403)
    Asistencia.objects.filter(alumno=alumno, fecha=fecha).delete()
    return JsonResponse({"success": True, "message": "Registro eliminado."})


# ============================================================
#                    CONFIGURACIÓN DOCENTE
# ============================================================

@rol_requerido("docente")
def configuracion_docente(request):
    return _configuracion_cuenta(request)

    docente = Docente.objects.select_related(
        "usuario"
    ).get(
        usuario=request.user
    )

    asignaciones = AsignacionDocente.objects.filter(
        docente=docente
    ).select_related(
        "docente",
        "curso"
    )

    if request.method == "POST":

        usuario = docente.usuario

        nombre_completo = request.POST.get(
            "nombre",
            ""
        ).strip()

        correo = request.POST.get(
            "correo",
            ""
        ).strip()

        telefono = request.POST.get(
            "telefono",
            ""
        ).strip()
        if len(telefono) > 30:
            messages.error(request, "El telefono no puede superar 30 caracteres.")
            return redirect("configuracion_docente")

        partes = nombre_completo.split(
            " ",
            1
        )

        usuario.first_name = (
            partes[0]
            if partes
            else ""
        )

        usuario.last_name = (
            partes[1]
            if len(partes) > 1
            else ""
        )

        if correo:

            usuario.email = correo

        usuario.save()

        docente.telefono = telefono or None
        docente.save(update_fields=["telefono"])

        messages.success(
            request,
            "Perfil actualizado correctamente."
        )

        return redirect(
            "configuracion_docente"
        )

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

@rol_requerido("administrador")
def carga_academica(request):

    docentes = Docente.objects.select_related(
        "usuario"
    ).all()

    filas = []

    for docente in docentes:

        asignaciones = AsignacionDocente.objects.filter(
            docente=docente
        ).select_related(
            "docente",
            "curso"
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
#                    HORARIOS DOCENTE
# ============================================================

@rol_requerido("docente")
def horarios_docente(request):

    # DOCENTE ACTUAL
    docente = Docente.objects.select_related(
        "usuario"
    ).get(
        usuario=request.user
    )

    # CURSOS ASIGNADOS (FUENTE 1: AsignacionDocente
    cursos_asignacion_ids = list(
        AsignacionDocente.objects
        .filter(
            docente_id=docente.id,
            curso__isnull=False
        )
        .values_list("curso_id", flat=True)
        .distinct()
    )

    # CURSOS CON HORARIOS (FUENTE 2: el propio docente tiene horarios creados)
    cursos_horario_ids = list(
        Horario.objects
        .filter(docente_id=docente.id)
        .values_list("curso_id", flat=True)
        .distinct()
    )

    # UNIMOS AMBAS FUENTES
    cursos_ids = list(
        set(list(cursos_asignacion_ids) + list(cursos_horario_ids))
    )

    cursos = Cursos.objects.filter(
        id__in=cursos_ids
    ).order_by("nombre")
    periodos = Periodo.objects.all().order_by("id")

    # HORARIOS DEL DOCENTE (solo los que él imparte)
    horarios = (
        Horario.objects
        .filter(
            docente_id=docente.id,
            curso_id__in=cursos_ids
        )
        .select_related(
            "periodo",
            "docente__usuario",
            "curso",
            "clase"
        )
        .order_by(
            "periodo__anio",
            "periodo__numero",
            "curso__nombre",
            "dia",
            "hora_inicio",
        )
    )

    horarios_data = []

    for horario in horarios:

        horarios_data.append({
            "id": horario.id,

            "periodo": horario.periodo_id,
            "periodoNumero": horario.periodo.numero,
            "periodoAnio": horario.periodo.anio,

            "docente": horario.docente_id,
            "docenteNombre": str(horario.docente),

            "curso": horario.curso_id,
            "cursoNombre": horario.curso.nombre,

            "clase": (
                horario.clase_id
                if horario.clase
                else None
            ),

            "claseNombre": (
                str(horario.clase)
                if horario.clase
                else ""
            ),

            "dia": horario.dia,
            "jornada": horario.jornada,

            "horaInicio": horario.hora_inicio.strftime("%H:%M"),
            "horaFin": horario.hora_fin.strftime("%H:%M"),
        })

    return render(
        request,
        "paneles/docentes/horarios_docente.html",
        {
            "docente": docente,
            "periodos": periodos,
            "cursos": cursos,
            "horarios_data": horarios_data,
        }
    )


@rol_requerido("docente")
def detalle_horario_docente(request, periodo_id, curso_id):

    # DOCENTE ACTUAL
    docente = Docente.objects.select_related(
        "usuario"
    ).get(
        usuario=request.user
    )

    # VERIFICAR QUE EL DOCENTE TENGA ASIGNACIÓN O HORARIOS EN ESE CURSO
    tiene_asignacion = AsignacionDocente.objects.filter(
        docente_id=docente.id,
        curso_id=curso_id
    ).exists()

    tiene_horario = Horario.objects.filter(
        docente_id=docente.id,
        curso_id=curso_id,
    ).exists()

    if not tiene_asignacion and not tiene_horario:
        messages.error(
            request,
            "No tienes permiso para ver el horario de este curso."
        )
        return redirect("horarios_docente")

    periodo = get_object_or_404(Periodo, pk=periodo_id)
    curso = get_object_or_404(Cursos, pk=curso_id)

    # SOLO HORARIOS DE ESTE DOCENTE EN EL PERIODO + CURSO SELECCIONADO
    horarios = (
        Horario.objects
        .filter(
            docente_id=docente.id,
            periodo_id=periodo.id,
            curso_id=curso.id,
        )
        .select_related(
            "periodo",
            "docente__usuario",
            "curso",
            "clase"
        )
        .order_by(
            "dia",
            "hora_inicio",
        )
    )

    horarios_data = []

    for horario in horarios:

        horarios_data.append({
            "id": horario.id,

            "periodo": horario.periodo_id,
            "periodoNumero": horario.periodo.numero,
            "periodoAnio": horario.periodo.anio,

            "docente": horario.docente_id,
            "docenteNombre": str(horario.docente),

            "curso": horario.curso_id,
            "cursoNombre": horario.curso.nombre,

            "clase": (
                horario.clase_id
                if horario.clase
                else None
            ),

            "claseNombre": (
                str(horario.clase)
                if horario.clase
                else ""
            ),

            "dia": horario.dia,
            "jornada": horario.jornada,

            "horaInicio": horario.hora_inicio.strftime("%H:%M"),
            "horaFin": horario.hora_fin.strftime("%H:%M"),
        })

    return render(
        request,
        "paneles/docentes/detalle_horario_docente.html",
        {
            "docente": docente,
            "periodo": periodo,
            "curso": curso,
            "horarios_data": horarios_data,
        }
    )


# ============================================================
#                    DASHBOARD ALUMNOS
# ============================================================

@rol_requerido("alumno")
def dashboard_alumnos(request):

    alumno = get_object_or_404(
        Alumnos.objects.select_related("usuario", "curso", "clase").prefetch_related("curso__clases"),
        usuario=request.user,
        activo=True,
    )
    clases_asignadas = (
        [alumno.clase]
        if alumno.clase_id
        else list(alumno.curso.clases.all()) if alumno.curso_id else []
    )
    alumno.clases_asignadas = clases_asignadas

    estadisticas_asistencia = Asistencia.objects.filter(alumno=alumno).aggregate(
        total=Count("id"),
        presentes=Count("id", filter=Q(estado="P")),
        tardanzas=Count("id", filter=Q(estado="T")),
        ausentes=Count("id", filter=Q(estado="A")),
    )
    presentes = estadisticas_asistencia["presentes"]
    tardanzas = estadisticas_asistencia["tardanzas"]
    ausentes = estadisticas_asistencia["ausentes"]
    total_asistencias = estadisticas_asistencia["total"]
    porcentaje_asistencia = (
        round((presentes + tardanzas) / total_asistencias * 100, 1)
        if total_asistencias else None
    )

    promedio_general = obtener_promedio_general_alumno(alumno)
    resumen_tareas = obtener_resumen_tareas_por_alumno([alumno]).get(
        alumno.id,
        {"total": 0, "entregadas": 0, "pendientes": 0},
    )

    notas_por_materia = defaultdict(list)
    calificaciones_tareas = Calificacion.objects.filter(
        alumno_id=alumno.usuario_id,
        nota__isnull=False,
    ).select_related("tarea__clase", "tarea__curso")
    calificaciones_actividades = CalificacionActividad.objects.filter(
        alumno_id=alumno.usuario_id,
        nota__isnull=False,
    ).select_related("actividad__clase", "actividad__curso")
    for calificacion in calificaciones_tareas:
        tarea = calificacion.tarea
        materia = (
            tarea.clase.titulo if tarea.clase_id
            else tarea.curso.nombre if tarea.curso_id
            else "Sin materia"
        )
        notas_por_materia[materia].append(float(calificacion.nota))
    for calificacion in calificaciones_actividades:
        actividad = calificacion.actividad
        materia = (
            actividad.clase.titulo if actividad.clase_id
            else actividad.curso.nombre if actividad.curso_id
            else "Sin materia"
        )
        notas_por_materia[materia].append(float(calificacion.nota))
    calificaciones = [
        {"materia": materia, "promedio": round(sum(notas) / len(notas), 2)}
        for materia, notas in sorted(notas_por_materia.items())
        if notas
    ]

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "alumnos"],
        fecha__gte=timezone.localdate(),
    ).order_by("fecha", F("hora_inicio").asc(nulls_last=True), "pk")

    return render(
        request,
        "paneles/alumnos/dashboard_alumnos.html",
        {
            "eventos": eventos,
            "alumno": alumno,
            "porcentaje_asistencia": porcentaje_asistencia,
            "promedio_general": float(promedio_general) if promedio_general is not None else None,
            "tareas_pendientes": resumen_tareas["pendientes"],
            "total_tareas": resumen_tareas["total"],
            "calificaciones": calificaciones,
            "total_logros": 0,
            "presentes": presentes,
            "tardanzas": tardanzas,
            "ausentes": ausentes,
        }
    )


# ============================================================
#                    MATERIAS ALUMNOS
# ============================================================

@rol_requerido("alumno")
def materias_alumnos(request):

    return render(
        request,
        "paneles/alumnos/materias_alumnos.html"
    )




# ============================================================
#                    CALIFICACIONES ALUMNOS
# ============================================================

@rol_requerido("alumno")
def calificaciones_alumnos(request):

    # --------------------------------------------------------
    # OBTENER ALUMNO LOGUEADO
    # --------------------------------------------------------

    alumno = get_object_or_404(
        Alumnos.objects.select_related(
            "usuario",
            "curso",
            "clase"
        ).prefetch_related("curso__clases"),
        usuario=request.user
    )
    clases_asignadas = (
        [alumno.clase]
        if alumno.clase_id
        else list(alumno.curso.clases.all()) if alumno.curso_id else []
    )

    # --------------------------------------------------------
    # CALIFICACIONES REALES DEL ALUMNO
    # --------------------------------------------------------
    # Se buscan directamente las calificaciones del usuario.
    # De esta forma no dependemos de que la tarea tenga
    # exactamente la misma clase o curso para mostrar la nota.

    calificaciones = (
        Calificacion.objects
        .filter(
            alumno=request.user
        )
        .select_related(
            "tarea",
            "tarea__docente",
            "tarea__curso",
            "tarea__clase"
        )
        .order_by(
            "-id"
        )
    )
    calificaciones = list(calificaciones)
    calificaciones_actividades = CalificacionActividad.objects.filter(
        alumno_id=alumno.usuario_id,
        nota__isnull=False,
    ).select_related("actividad__docente__usuario").order_by(
        "-actividad__fecha", "-id"
    )
    for calificacion_actividad in calificaciones_actividades:
        actividad = calificacion_actividad.actividad
        calificaciones.append(SimpleNamespace(
            tarea=SimpleNamespace(
                titulo=actividad.nombre,
                descripcion=actividad.descripcion,
                docente=actividad.docente,
                fecha_entrega=actividad.fecha,
            ),
            nota=calificacion_actividad.nota,
            tipo=actividad.tipo or "Actividad",
        ))
    

    # --------------------------------------------------------
    # FILAS PARA LA TABLA NUEVA
    # --------------------------------------------------------

    filas = []

    for calificacion in calificaciones:

        tarea = calificacion.tarea

        filas.append({
            "tipo": "Tarea",
            "nombre": tarea.titulo,
            "descripcion": tarea.descripcion,
            "docente": tarea.docente,
            "fecha": tarea.fecha_entrega,
            "nota": calificacion.nota,
        })

    # --------------------------------------------------------
    # REGISTROS PARA COMPATIBILIDAD CON LA PLANTILLA
    # --------------------------------------------------------
    # También enviamos "registros" por si la plantilla actual
    # utiliza esa variable.

    registros = []

    for calificacion in calificaciones:

        registros.append({
            "tarea": calificacion.tarea,
            "calificacion": calificacion,
            "nota": calificacion.nota,
        })

    # --------------------------------------------------------
    # PROMEDIO
    # --------------------------------------------------------

    notas = [
        float(calificacion.nota)
        for calificacion in calificaciones
        if calificacion.nota is not None
    ]

    promedio = obtener_promedio_general_alumno(alumno)

    # --------------------------------------------------------
    # ESTADO ACADÉMICO
    # --------------------------------------------------------

    if promedio is None:

        estado = "Sin calificaciones"

    elif promedio >= 4.5:

        estado = "Superior"

    elif promedio >= 4.0:

        estado = "Alto"

    elif promedio >= 3.0:

        estado = "Básico"

    else:

        estado = "Bajo"

    # --------------------------------------------------------
    # ESTADÍSTICAS
    # --------------------------------------------------------

    total_calificaciones = len(notas)

    resumen_tareas = obtener_resumen_tareas_por_alumno([alumno]).get(
        alumno.id,
        {"total": 0, "entregadas": 0, "pendientes": 0},
    )
    total_tareas = resumen_tareas["total"]

    tareas_calificadas = total_calificaciones

    tareas_pendientes = resumen_tareas["pendientes"]

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    context = {

        "alumno": alumno,

        "curso": alumno.curso,

        "clase": alumno.clase,

        "clases_asignadas": clases_asignadas,

        # Tabla actual
        "filas": filas,

        # Compatibilidad con versiones anteriores
        "registros": registros,

        # Calificaciones originales
        "calificaciones": calificaciones,

        # Estadísticas
        "promedio": promedio,

        "estado": estado,

        "total_calificaciones": total_calificaciones,

        "total_tareas": total_tareas,

        "tareas_calificadas": tareas_calificadas,

        "tareas_pendientes": tareas_pendientes,

    }

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(
        request,
        "paneles/alumnos/calificaciones_alumnos.html",
        context
    )


# ============================================================
#                    ASISTENCIA ALUMNOS
# ============================================================

@rol_requerido("alumno")
def asistencia_alumnos(request):
    alumno = get_object_or_404(
        Alumnos.objects.select_related("usuario", "curso"),
        usuario=request.user,
        activo=True,
    )
    asistencias = Asistencia.objects.filter(alumno=alumno).select_related("curso").order_by("-fecha")
    presentes = asistencias.filter(estado="P").count()
    tardanzas = asistencias.filter(estado="T").count()
    ausentes = asistencias.filter(estado="A").count()
    total = asistencias.count()
    porcentaje_asistencia = round(((presentes + tardanzas) / total) * 100, 1) if total else None
    return render(request, "paneles/alumnos/asistencia_alumno.html", {
        "alumno": alumno,
        "asistencias": asistencias[:100],
        "presentes": presentes,
        "tardanzas": tardanzas,
        "ausentes": ausentes,
        "total": total,
        "porcentaje_asistencia": porcentaje_asistencia,
    })


# ============================================================
#                    LOGROS ALUMNOS
# ============================================================

@rol_requerido("alumno")
def logros_alumnos(request):

    return render(
        request,
        "paneles/alumnos/logros_alumnos.html"
    )


# ============================================================
#                    CONFIGURACIÓN ALUMNOS
# ============================================================

@rol_requerido("alumno")
def configuracion_alumnos(request):
    return _configuracion_cuenta(request)


@login_required
def _configuracion_cuenta(request):
    rol = (
        "administrador"
        if request.user.is_superuser
        else request.user.rol.nombre.lower().strip() if request.user.rol else ""
    )
    bases = {
        "docente": "paneles/docentes/base.html",
        "alumno": "paneles/alumnos/base.html",
        "acudiente": "paneles/acudientes/base.html",
        "administrador": "admin/base_admin.html",
    }
    if rol not in bases:
        return redirect("redireccionar_por_rol")

    perfil = None
    if rol == "docente":
        perfil = Docente.objects.filter(usuario=request.user).first()
    elif rol == "alumno":
        perfil = Alumnos.objects.filter(usuario=request.user).first()
    elif rol == "acudiente":
        perfil = Acudiente.objects.filter(usuario=request.user).first()

    perfil_initial = {}
    if perfil and not request.user.telefono:
        perfil_initial["telefono"] = getattr(perfil, "telefono", "") or ""
    if perfil and not request.user.direccion:
        perfil_initial["direccion"] = getattr(perfil, "direccion", "") or ""
    if perfil and not request.user.fecha_nacimiento and isinstance(perfil, Alumnos):
        perfil_initial["fecha_nacimiento"] = perfil.fecha_nacimiento
    fecha_nacimiento_cuenta = request.user.fecha_nacimiento
    if not fecha_nacimiento_cuenta and isinstance(perfil, Alumnos):
        fecha_nacimiento_cuenta = perfil.fecha_nacimiento
    edad_actual = None
    if fecha_nacimiento_cuenta:
        hoy = timezone.localdate()
        edad_actual = hoy.year - fecha_nacimiento_cuenta.year - (
            (hoy.month, hoy.day) < (fecha_nacimiento_cuenta.month, fecha_nacimiento_cuenta.day)
        )
    perfil_form = CuentaPerfilForm(instance=request.user, initial=perfil_initial)
    password_form = PasswordChangeForm(user=request.user)
    solicitud_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if request.method == "POST" and request.POST.get("action") == "profile":
        perfil_form = CuentaPerfilForm(
            request.POST,
            instance=request.user,
            initial=perfil_initial,
        )
        if perfil_form.is_valid():
            usuario = perfil_form.save()
            telefono = usuario.telefono or None
            direccion = usuario.direccion or ""
            if isinstance(perfil, Docente):
                perfil.telefono = telefono or None
                perfil.direccion = direccion
                perfil.save(update_fields=["telefono", "direccion"])
            elif isinstance(perfil, (Alumnos, Acudiente)):
                perfil.telefono = telefono or ""
                perfil.direccion = direccion
                perfil.save(update_fields=["telefono", "direccion"])
            if isinstance(perfil, Alumnos):
                perfil.fecha_nacimiento = usuario.fecha_nacimiento
                perfil.save(update_fields=["fecha_nacimiento"])
            if solicitud_ajax:
                return JsonResponse({"ok": True, "message": "Tus datos se guardaron correctamente."})
            messages.success(request, "Tu perfil se guardó correctamente.")
            return redirect(request.path)
        if solicitud_ajax:
            return JsonResponse({
                "ok": False,
                "message": "Revisa los campos marcados e inténtalo de nuevo.",
                "errors": perfil_form.errors.get_json_data(),
            }, status=400)
        messages.error(request, "Revisa los campos del perfil e inténtalo de nuevo.")
    elif request.method == "POST" and request.POST.get("action") == "password":
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            usuario = password_form.save()
            update_session_auth_hash(request, usuario)
            if solicitud_ajax:
                return JsonResponse({"ok": True, "message": "Tu contraseña se actualizó correctamente."})
            messages.success(request, "Tu contraseña se actualizó correctamente.")
            return redirect(request.path)
        if solicitud_ajax:
            return JsonResponse({
                "ok": False,
                "message": "No se pudo cambiar la contraseña. Revisa los datos ingresados.",
                "errors": password_form.errors.get_json_data(),
            }, status=400)
        messages.error(request, "No se pudo cambiar la contraseña. Revisa los datos ingresados.")

    for campo in password_form.fields.values():
        campo.widget.attrs.update({"class": "account-input", "autocomplete": "new-password"})

    return render(request, "paneles/configuracion_cuenta.html", {
        "perfil": perfil,
        "perfil_form": perfil_form,
        "password_form": password_form,
        "base_template": bases[rol],
        "rol_nombre": rol.capitalize(),
        "cuenta_usuario": request.user,
        "fecha_nacimiento_cuenta": fecha_nacimiento_cuenta,
        "edad_actual": edad_actual,
    })


def configuracion_acudiente(request):
    return _configuracion_cuenta(request)


def configuracion_administrador(request):
    return _configuracion_cuenta(request)


def configuracion_cuenta(request):
    return _configuracion_cuenta(request)


# ============================================================
#                    HORARIOS ALUMNOS
# ============================================================

@rol_requerido("alumno")
def horarios_alumnos(request):

    alumno = get_object_or_404(
        Alumnos.objects.select_related(
            "usuario",
            "curso",
        ),
        usuario=request.user,
        activo=True,
    )

    periodos = (
        Periodo.objects
        .filter(
            activo=True,
        )
        .order_by(
            "-anio",
            "-numero",
        )
    )

    horarios = (
        Horario.objects
        .filter(
            curso_id=alumno.curso_id,
        )
        .select_related(
            "periodo",
            "docente__usuario",
            "curso",
            "clase",
        )
        .order_by(
            "dia",
            "hora_inicio",
        )
    )

    horarios_data = []

    for horario in horarios:

        horarios_data.append({
            "id": horario.id,

            "periodo": horario.periodo_id,
            "periodoNumero": horario.periodo.numero if horario.periodo_id else None,
            "periodoAnio": horario.periodo.anio if horario.periodo_id else None,

            "docente": horario.docente_id,
            "docenteNombre": str(horario.docente) if horario.docente_id else "",

            "curso": horario.curso_id,
            "cursoNombre": horario.curso.nombre if horario.curso_id else "",

            "clase": horario.clase_id,
            "claseNombre": str(horario.clase) if horario.clase_id else "",

            "dia": horario.dia,
            "jornada": horario.jornada,

            "horaInicio": horario.hora_inicio.strftime("%H:%M"),
            "horaFin": horario.hora_fin.strftime("%H:%M"),
        })

    return render(
        request,
        "paneles/alumnos/horarios_alumnos.html",
        {
            "alumno": alumno,
            "periodos": periodos,
            "horarios_data": horarios_data,
        }
    )


# ============================================================
#                    DASHBOARD ACUDIENTE
# ============================================================

@rol_requerido("acudiente")
def dashboard_acudiente(request):
    acudiente, _ = Acudiente.objects.get_or_create(
        usuario=request.user,
        defaults={
            "telefono": request.user.telefono,
            "direccion": request.user.direccion,
        },
    )

    if not acudiente.activo:
        return redirect("login")

    relaciones = list(
        AcudienteAlumno.objects.filter(
            acudiente=acudiente,
            autorizado=True,
            alumno__activo=True,
        )
        .select_related(
            "alumno",
            "alumno__usuario",
            "alumno__curso",
            "alumno__clase",
        )
        .prefetch_related("alumno__curso__clases")
        .order_by("alumno__usuario__first_name", "alumno__usuario__last_name")
    )

    alumnos_ids = [relacion.alumno_id for relacion in relaciones]
    alumnos_relacionados = [relacion.alumno for relacion in relaciones]
    resumen_tareas_por_alumno = obtener_resumen_tareas_por_alumno(alumnos_relacionados)
    asistencia_por_alumno = {
        item["alumno_id"]: item
        for item in Asistencia.objects.filter(alumno_id__in=alumnos_ids)
        .values("alumno_id")
        .annotate(
            total=Count("id"),
            presentes=Count("id", filter=Q(estado="P")),
            tardanzas=Count("id", filter=Q(estado="T")),
        )
    }
    alumnos = []
    for relacion in relaciones:
        alumno = relacion.alumno
        promedio = obtener_promedio_general_alumno(alumno)
        promedio = float(promedio) if promedio is not None else None

        asistencia = asistencia_por_alumno.get(alumno.id, {})
        total_asistencias = asistencia.get("total", 0)
        presentes = asistencia.get("presentes", 0)
        tardanzas = asistencia.get("tardanzas", 0)
        porcentaje_asistencia = (
            round(((presentes + tardanzas) / total_asistencias) * 100, 1)
            if total_asistencias else None
        )

        alumno.promedio = promedio
        alumno.porcentaje_asistencia = porcentaje_asistencia
        alumno.tareas_pendientes = resumen_tareas_por_alumno.get(
            alumno.id, {"pendientes": 0}
        )["pendientes"]
        alumno.clases_asignadas = (
            [alumno.clase]
            if alumno.clase_id
            else list(alumno.curso.clases.all()) if alumno.curso_id else []
        )
        alumno.parentesco = relacion.parentesco
        alumnos.append(alumno)

    eventos_query = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "acudientes"],
        fecha__gte=timezone.localdate(),
    ).order_by("fecha", "hora_inicio")
    eventos_proximos = list(eventos_query[:5])
    total_eventos_proximos = eventos_query.count()
    promedios = [alumno.promedio for alumno in alumnos if alumno.promedio is not None]
    promedio_general = round(sum(promedios) / len(promedios), 2) if promedios else None
    alumnos_alerta = sum(
        1 for alumno in alumnos
        if alumno.porcentaje_asistencia is not None and alumno.porcentaje_asistencia < 80
    )

    return render(
        request,
        "paneles/acudientes/dashboard_acudiente.html",
        {
            "acudiente": acudiente,
            "alumnos": alumnos,
            "eventos_proximos": eventos_proximos,
            "total_eventos_proximos": total_eventos_proximos,
            "promedio_general": promedio_general,
            "alumnos_alerta": alumnos_alerta,
        },
    )

@rol_requerido("acudiente")
def horario_alumno_acudiente(request, alumno_id):
    acudiente = get_object_or_404(
        Acudiente,
        usuario=request.user,
        activo=True,
    )
    relacion = get_object_or_404(
        AcudienteAlumno.objects.select_related(
            "alumno__usuario",
            "alumno__curso",
            "alumno__clase",
        ),
        acudiente=acudiente,
        alumno_id=alumno_id,
        alumno__activo=True,
        autorizado=True,
    )
    alumno = relacion.alumno
    periodos = Periodo.objects.filter(activo=True).order_by("-anio", "-numero")
    periodo_id = request.GET.get("periodo")
    periodo = get_object_or_404(periodos, pk=periodo_id) if periodo_id else periodos.first()

    horarios = Horario.objects.none()
    if alumno.curso_id and periodo:
        horarios = Horario.objects.filter(
            curso_id=alumno.curso_id,
            periodo=periodo,
        )
        if alumno.clase_id:
            horarios = horarios.filter(Q(clase_id=alumno.clase_id) | Q(clase__isnull=True))
        horarios = horarios.select_related(
            "periodo", "docente__usuario", "curso", "clase"
        ).order_by("dia", "hora_inicio")

    return render(request, "paneles/acudientes/horario_alumno.html", {
        "alumno": alumno,
        "periodos": periodos,
        "periodo": periodo,
        "horarios": horarios,
    })


@rol_requerido("acudiente")
def eventos_acudiente(request):
    acudiente, _ = Acudiente.objects.get_or_create(
        usuario=request.user,
        defaults={
            "telefono": request.user.telefono,
            "direccion": request.user.direccion,
        },
    )
    if not acudiente.activo:
        return redirect("login")

    eventos = Evento.objects.filter(
        publicado=True,
        publico__in=["todos", "acudientes"],
    ).order_by("fecha", "hora_inicio")
    hoy = timezone.localdate()
    return render(request, "paneles/acudientes/eventos_acudiente.html", {
        "eventos_proximos": eventos.filter(fecha__gte=hoy),
        "eventos_pasados": eventos.filter(fecha__lt=hoy).order_by("-fecha", "-hora_inicio")[:10],
    })


# ============================================================
#                    DETALLE DEL ALUMNO
# ============================================================

@rol_requerido("acudiente")
def detalle_alumno_acudiente(
    request,
    alumno_id
):

    acudiente, _ = Acudiente.objects.get_or_create(
        usuario=request.user,
        defaults={
            "telefono": request.user.telefono,
            "direccion": request.user.direccion,
        },
    )

    if not acudiente.activo:
        return redirect("login")

    relacion = get_object_or_404(
        AcudienteAlumno.objects.select_related(
            "alumno",
            "alumno__usuario",
            "alumno__curso",
            "alumno__clase",
        ).prefetch_related("alumno__curso__clases"),
        acudiente=acudiente,
        alumno_id=alumno_id,
        alumno__activo=True,
        autorizado=True
    )

    alumno = relacion.alumno
    alumno.clases_asignadas = (
        [alumno.clase]
        if alumno.clase_id
        else list(alumno.curso.clases.all()) if alumno.curso_id else []
    )

    # -------------------------------------------------
    # CALIFICACIONES
    # -------------------------------------------------

    calificaciones_tareas = (
        Calificacion.objects
        .filter(alumno_id=alumno.usuario_id, nota__isnull=False)
        .select_related("tarea", "tarea__curso", "tarea__clase")
        .order_by("-id")
    )
    calificaciones_actividades = (
        CalificacionActividad.objects
        .filter(alumno_id=alumno.usuario_id, nota__isnull=False)
        .select_related("actividad", "actividad__curso", "actividad__clase")
        .order_by("-actividad__fecha", "-id")
    )
    calificaciones = [
        {"nombre": calificacion.tarea.titulo, "curso": calificacion.tarea.curso, "nota": calificacion.nota}
        for calificacion in calificaciones_tareas
    ] + [
        {"nombre": calificacion.actividad.nombre, "curso": calificacion.actividad.curso, "nota": calificacion.nota}
        for calificacion in calificaciones_actividades
    ]
    promedio = obtener_promedio_general_alumno(alumno)
    promedio = float(promedio) if promedio is not None else None

    # -------------------------------------------------
    # ASISTENCIA
    # -------------------------------------------------

    asistencias = (
        Asistencia.objects
        .filter(
            alumno=alumno
        )
        .select_related(
            "curso"
        )
        .order_by(
            "-fecha"
        )
    )

    total = asistencias.count()

    presentes = (
        asistencias
        .filter(
            estado="P"
        )
        .count()
    )

    tardanzas = asistencias.filter(estado="T").count()

    ausentes = (
        asistencias
        .filter(
            estado="A"
        )
        .count()
    )

    porcentaje_asistencia = (

        round(
            ((presentes + tardanzas) / total) * 100,
            1
        )

        if total > 0

        else None
    )

    return render(
        request,
        "paneles/acudientes/detalle_alumno.html",
        {
            "acudiente": acudiente,
            "relacion": relacion,
            "alumno": alumno,
            "calificaciones": calificaciones,
            "promedio": promedio,
            "asistencias": asistencias,
            "total": total,
            "presentes": presentes,
            "tardanzas": tardanzas,
            "ausentes": ausentes,
            "porcentaje_asistencia": porcentaje_asistencia,
        }
    )
