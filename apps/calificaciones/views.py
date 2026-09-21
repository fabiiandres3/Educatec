from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from apps.alumnos.models import Alumnos
from apps.docentes.models import Docente
from apps.tareas.models import (
    Tareas, Calificacion, ActividadCalificacion, CalificacionActividad,
)
from apps.horario.models import Periodo
from django.utils.dateparse import parse_date
from django.utils import timezone

from .services import (
    obtener_asignaciones_docente,
    obtener_libro_calificaciones,
    obtener_promedio_general_alumno,
)


# ============================================================
# CALIFICACIONES DEL DOCENTE
# ============================================================

@login_required
def calificaciones_docente(request):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # ============================================================
    # ASIGNACIONES DEL DOCENTE
    # ============================================================

    asignaciones = obtener_asignaciones_docente(docente)

    # ============================================================
    # ASIGNACIÓN SELECCIONADA
    # ============================================================

    asignacion_id = request.GET.get("asignacion")

    asignacion_actual = None

    if asignacion_id:
        asignacion_actual = get_object_or_404(
            asignaciones,
            id=asignacion_id
        )

    # ============================================================
    # DATOS INICIALES
    # ============================================================

    alumnos = []
    tareas = []
    actividades = []

    # ============================================================
    # CURSO ACTUAL
    # ============================================================

    curso_actual = (
        asignacion_actual.curso
        if asignacion_actual
        else None
    )

    # ============================================================
    # OBTENER CALIFICACIONES
    # ============================================================

    if asignacion_actual:

        alumnos, tareas, actividades = obtener_libro_calificaciones(
            asignacion_actual
        )

    # ============================================================
    # ESTUDIANTES EN RIESGO
    # ============================================================

    estudiantes_riesgo = [
        alumno
        for alumno in alumnos
        if getattr(
            alumno,
            "en_riesgo",
            False
        )
    ]

    # ============================================================
    # CONTEXTO
    # ============================================================

    context = {

        "docente": docente,

        "asignaciones": asignaciones,

        "asignacion_actual": asignacion_actual,

        "curso_actual": curso_actual,

        # AsignacionDocente ya NO tiene clase
        "clase_actual": None,

        "tareas": tareas,
        "actividades": actividades,

        "alumnos": alumnos,

        "estudiantes_riesgo": estudiantes_riesgo,

        "total_estudiantes": len(alumnos),

        "total_tareas": len(tareas) + len(actividades),

        "total_riesgo": len(
            estudiantes_riesgo
        ),
    }

    return render(
        request,
        "paneles/docentes/calificaciones_docente.html",
        context
    )


# ============================================================
# EDITAR CALIFICACIÓN (CORREGIDA PARA SOPORTAR FETCH / AJAX)
# ============================================================

@login_required
def editar_calificacion(request, calificacion_id):

    # Detectar si la petición viene de un fetch/AJAX de JavaScript
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    calificacion = get_object_or_404(
        Calificacion,
        id=calificacion_id
    )

    tarea = calificacion.tarea

    # Verificamos que la tarea pertenezca al docente
    if tarea.docente_id != docente.id:
        if is_ajax:
            return JsonResponse({"ok": False, "mensaje": "No tienes permiso para modificar esta calificación."}, status=403)

        messages.error(
            request,
            "No tienes permiso para modificar esta calificación."
        )
        return redirect("calificaciones_docente")

    if request.method == "POST":

        nota = request.POST.get("nota")

        try:
            nota_decimal = Decimal(
                nota.replace(",", ".")
            )
        except (InvalidOperation, AttributeError):
            if is_ajax:
                return JsonResponse({"ok": False, "mensaje": "La nota ingresada no es válida."}, status=400)

            messages.error(
                request,
                "La nota ingresada no es válida."
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    "calificaciones_docente"
                )
            )

        # Validar rango
        if (
            nota_decimal < Decimal("0")
            or nota_decimal > Decimal("5")
        ):
            if is_ajax:
                return JsonResponse({"ok": False, "mensaje": "La nota debe estar entre 0.00 y 5.00."}, status=400)

            messages.error(
                request,
                "La nota debe estar entre 0.00 y 5.00."
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    "calificaciones_docente"
                )
            )

        calificacion.nota = nota_decimal

        calificacion.save(
            update_fields=["nota"]
        )

        if is_ajax:
            return JsonResponse({
                "ok": True,
                "mensaje": "La calificación fue actualizada correctamente.",
                "nota": str(calificacion.nota)
            })

        messages.success(
            request,
            "La calificación fue actualizada correctamente."
        )

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "calificaciones_docente"
            )
        )

    if is_ajax:
        return JsonResponse({"ok": False, "mensaje": "Método no permitido."}, status=405)

    return redirect("calificaciones_docente")


# ============================================================
# GUARDAR CALIFICACIÓN
# ============================================================

@login_required
def guardar_calificacion(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Método no permitido."
            },
            status=405
        )

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    alumno_id = request.POST.get("alumno_id")
    tarea_id = request.POST.get("tarea_id")
    nota = request.POST.get("nota")

    if not alumno_id or not tarea_id:

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Faltan datos."
            },
            status=400
        )

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    if tarea.docente_id != docente.id:

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "No puedes calificar esta tarea."
            },
            status=403
        )

    alumno = get_object_or_404(
        Alumnos,
        usuario_id=alumno_id,
        activo=True
    )

    if alumno.curso_id != tarea.curso_id:

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "El alumno no pertenece al curso de la tarea."
            },
            status=403
        )

    if nota is None or nota.strip() == "":

        Calificacion.objects.filter(
            alumno_id=alumno_id,
            tarea_id=tarea_id
        ).delete()

        return JsonResponse(
            {
                "ok": True,
                "mensaje": "Calificación eliminada."
            }
        )

    try:

        nota_decimal = Decimal(
            nota.replace(",", ".")
        )

    except (
        InvalidOperation,
        AttributeError
    ):

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "La calificación no es válida."
            },
            status=400
        )

    if nota_decimal < Decimal("0"):

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "La nota no puede ser menor que 0."
            },
            status=400
        )

    if nota_decimal > Decimal("5"):

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "La nota no puede ser mayor que 5."
            },
            status=400
        )

    calificacion, creada = (
        Calificacion.objects.update_or_create(
            alumno_id=alumno_id,
            tarea_id=tarea_id,
            defaults={
                "nota": nota_decimal
            }
        )
    )

    return JsonResponse(
        {
            "ok": True,
            "mensaje": (
                "Calificación guardada correctamente."
            ),
            "nota": str(calificacion.nota)
        }
    )


# ============================================================
# CALIFICACIONES DEL ALUMNO
# ============================================================

@login_required
def calificaciones_alumnos(request):


    alumno = get_object_or_404(
        Alumnos.objects.select_related(
            "usuario",
            "curso"
        ),
        usuario=request.user
    )



    # TODAS las calificaciones del usuario, sin filtrar por curso/clase
    calificaciones = Calificacion.objects.filter(
        alumno=request.user
    ).select_related(
        "tarea",
        "tarea__curso",
        "tarea__clase",
        "tarea__docente"
    ).order_by("-id")

    print("TOTAL CALIFICACIONES:", calificaciones.count())

    for cal in calificaciones:
        print(
            "CALIFICACION:",
            cal.id,
            "| ALUMNO:",
            cal.alumno_id,
            "| TAREA:",
            cal.tarea_id,
            "| NOTA:",
            cal.nota,
            "| CURSO TAREA:",
            cal.tarea.curso_id,
            "| CLASE TAREA:",
            cal.tarea.clase_id,
        )

    registros = []

    for calificacion in calificaciones:

        registros.append({
            "tarea": calificacion.tarea,
            "calificacion": calificacion,
            "nota": calificacion.nota,
        })

    notas = [
        Decimal(str(cal.nota))
        for cal in calificaciones
        if cal.nota is not None
    ]
    promedio = obtener_promedio_general_alumno(alumno)

    if promedio is None:
        estado = "Sin calificaciones"
    elif promedio >= Decimal("4.5"):
        estado = "Superior"
    elif promedio >= Decimal("4.0"):
        estado = "Alto"
    elif promedio >= Decimal("3.0"):
        estado = "Básico"
    else:
        estado = "Bajo"

    total_tareas = calificaciones.count()
    tareas_calificadas = len(notas)
    tareas_pendientes = 0

    context = {
        "alumno": alumno,
        "curso": alumno.curso,
        "clase": None,
        "registros": registros,
        "calificaciones": calificaciones,
        "promedio": promedio,
        "estado": estado,
        "total_tareas": total_tareas,
        "tareas_calificadas": tareas_calificadas,
        "tareas_pendientes": tareas_pendientes,
    }

    return render(
        request,
        "paneles/alumnos/calificaciones_alumnos.html",
        context
    )


@login_required
def crear_actividad_calificacion(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "mensaje": "Método no permitido."}, status=405)
    docente = get_object_or_404(Docente, usuario=request.user)
    asignacion = get_object_or_404(obtener_asignaciones_docente(docente), pk=request.POST.get("asignacion_id"))
    nombre = (request.POST.get("nombre") or "").strip()
    fecha = parse_date(request.POST.get("fecha") or "")
    if not nombre:
        return JsonResponse({"ok": False, "mensaje": "Escribe el nombre de la actividad."}, status=400)
    if request.POST.get("fecha") and not fecha:
        return JsonResponse({"ok": False, "mensaje": "La fecha no es válida."}, status=400)
    periodo = None
    if request.POST.get("periodo_id"):
        periodo = get_object_or_404(Periodo, pk=request.POST["periodo_id"])
    actividad = ActividadCalificacion.objects.create(
        docente=docente, curso=asignacion.curso, clase=asignacion.clase,
        periodo=periodo, nombre=nombre, tipo=(request.POST.get("tipo") or "Actividad")[:50],
        descripcion=(request.POST.get("descripcion") or "").strip(),
        fecha=fecha or timezone.localdate(),
    )
    return JsonResponse({"ok": True, "actividad_id": actividad.id})


@login_required
def guardar_calificacion_actividad(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "mensaje": "Método no permitido."}, status=405)
    docente = get_object_or_404(Docente, usuario=request.user)
    actividad = get_object_or_404(ActividadCalificacion, pk=request.POST.get("actividad_id"), docente=docente, activa=True)
    alumno = get_object_or_404(Alumnos, usuario_id=request.POST.get("alumno_id"), curso=actividad.curso, activo=True)
    nota = (request.POST.get("nota") or "").strip()
    if not nota:
        CalificacionActividad.objects.filter(actividad=actividad, alumno_id=alumno.usuario_id).delete()
        return JsonResponse({"ok": True, "nota": None})
    try:
        nota_decimal = Decimal(nota.replace(",", "."))
    except (InvalidOperation, AttributeError):
        return JsonResponse({"ok": False, "mensaje": "La nota no es válida."}, status=400)
    if not Decimal("0") <= nota_decimal <= Decimal("5"):
        return JsonResponse({"ok": False, "mensaje": "La nota debe estar entre 0.00 y 5.00."}, status=400)
    calificacion, _ = CalificacionActividad.objects.update_or_create(
        actividad=actividad, alumno_id=alumno.usuario_id, defaults={"nota": nota_decimal}
    )
    return JsonResponse({"ok": True, "nota": str(calificacion.nota)})
