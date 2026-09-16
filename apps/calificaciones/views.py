from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from apps.alumnos.models import Alumnos
from apps.docentes.models import Docente
from apps.tareas.models import Tareas, Calificacion

from .services import (
    obtener_asignaciones_docente,
    obtener_libro_calificaciones,
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

    asignaciones = obtener_asignaciones_docente(docente)

    asignacion_id = request.GET.get("asignacion")

    asignacion_actual = None
    alumnos = []
    tareas = []

    if asignacion_id:

        asignacion_actual = get_object_or_404(
            asignaciones,
            id=asignacion_id
        )

        alumnos, tareas = obtener_libro_calificaciones(
            asignacion_actual
        )

    estudiantes_riesgo = [
        alumno
        for alumno in alumnos
        if getattr(alumno, "en_riesgo", False)
    ]

    context = {
        "asignaciones": asignaciones,
        "asignacion_actual": asignacion_actual,

        "curso_actual": (
            asignacion_actual.clase.curso
            if asignacion_actual
            else None
        ),

        "clase_actual": (
            asignacion_actual.clase
            if asignacion_actual
            else None
        ),

        "tareas": tareas,
        "alumnos": alumnos,

        "estudiantes_riesgo": estudiantes_riesgo,

        "total_estudiantes": len(alumnos),
        "total_tareas": len(tareas),
        "total_riesgo": len(estudiantes_riesgo),
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
            "curso",
            "clase"
        ),
        usuario=request.user
    )

    tareas = Tareas.objects.filter(
        activa=True,
        curso_id=alumno.curso_id,
        clase_id=alumno.clase_id
    ).select_related(
        "docente",
        "clase",
        "curso"
    ).order_by(
        "fecha_entrega",
        "titulo"
    )

    calificaciones = Calificacion.objects.filter(
        alumno=request.user,
        tarea__in=tareas
    ).select_related(
        "tarea"
    )

    calificaciones_dict = {
        calificacion.tarea_id: calificacion
        for calificacion in calificaciones
    }

    registros = []
    notas = []

    for tarea in tareas:

        calificacion = calificaciones_dict.get(tarea.id)

        if calificacion:

            nota = calificacion.nota

            notas.append(
                Decimal(str(nota))
            )

        else:

            nota = None

        registros.append({
            "tarea": tarea,
            "calificacion": calificacion,
            "nota": nota,
        })

    if notas:

        promedio = (
            sum(notas) / Decimal(len(notas))
        ).quantize(
            Decimal("0.01")
        )

    else:

        promedio = None

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

    total_tareas = tareas.count()

    tareas_calificadas = len(notas)

    tareas_pendientes = (
        total_tareas - tareas_calificadas
    )

    context = {
        "alumno": alumno,
        "curso": alumno.curso,
        "clase": alumno.clase,
        "registros": registros,
        "tareas": tareas,
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