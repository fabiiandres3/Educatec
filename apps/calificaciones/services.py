from decimal import Decimal

from django.db.models import Q

from apps.alumnos.models import Alumnos
from apps.docentes.models import AsignacionDocente
from apps.tareas.models import (
    Tareas, Calificacion, ActividadCalificacion, CalificacionActividad,
)


def obtener_asignaciones_docente(docente):
    return (
        AsignacionDocente.objects
        .filter(
            docente=docente
        )
        .select_related(
            "docente",
            "curso",
            "clase"
        )
    )



def _obtener_tareas_asignacion(asignacion, periodo=None):
    """Tareas que la tabla de calificaciones atribuye a una asignación."""
    filtros = {
        "docente": asignacion.docente,
        "curso_id": asignacion.curso_id,
    }
    if asignacion.clase_id:
        # Las tareas creadas antes de vincular la materia quedaron con
        # ``clase=None``. Se conservan en el libro del mismo docente y curso
        # para no ocultar calificaciones ya registradas. Las tareas nuevas se
        # guardan siempre con la materia de la asignación.
        tareas = Tareas.objects.filter(**filtros).filter(
            Q(clase_id=asignacion.clase_id) | Q(clase__isnull=True)
        )
    else:
        tareas = Tareas.objects.filter(**filtros)
    if periodo:
        # Las tareas nuevas se filtran por su FK explícita. Las tareas
        # históricas sin período deben seguir contando: la app de
        # Calificaciones las muestra y el boletín debe usar esa misma fuente.
        # No es seguro descartarlas por una fecha de entrega que pudo haber
        # sido registrada fuera del rango configurado posteriormente.
        tareas = tareas.filter(
            Q(periodo=periodo)
            | Q(periodo__isnull=True)
        )
    return tareas.select_related("clase").order_by("fecha_entrega", "titulo")


def _obtener_actividades_asignacion(asignacion, periodo=None):
    """Actividades presenciales/manuales de una asignación."""
    filtros = {
        "docente": asignacion.docente,
        "curso_id": asignacion.curso_id,
    }
    if asignacion.clase_id:
        actividades = ActividadCalificacion.objects.filter(**filtros).filter(
            Q(clase_id=asignacion.clase_id) | Q(clase__isnull=True)
        )
    else:
        actividades = ActividadCalificacion.objects.filter(**filtros)
    if periodo:
        actividades = actividades.filter(
            Q(periodo=periodo)
            | Q(periodo__isnull=True)
        )
    return actividades.order_by("fecha", "nombre")


def calcular_promedio_calificaciones(calificaciones):
    """Regla única de promedio utilizada por calificaciones y boletín."""
    notas = [Decimal(str(calificacion.nota)) for calificacion in calificaciones if calificacion.nota is not None]
    if not notas:
        return None
    return (sum(notas) / Decimal(len(notas))).quantize(Decimal("0.01"))


def obtener_promedio_alumno_asignacion(alumno, asignacion, periodo=None):
    tareas = _obtener_tareas_asignacion(asignacion, periodo)
    actividades = _obtener_actividades_asignacion(asignacion, periodo)
    return calcular_promedio_calificaciones(
        list(Calificacion.objects.filter(alumno_id=alumno.usuario_id, tarea__in=tareas))
        + list(CalificacionActividad.objects.filter(
            alumno_id=alumno.usuario_id, actividad__in=actividades
        ))
    )


def obtener_promedio_general_alumno(alumno, periodo=None, curso=None):
    """Promedio general con la misma colección que ve el alumno.

    Al pedir un boletín se pasa explícitamente su curso y período; sin esos
    argumentos conserva el comportamiento histórico de calificaciones.
    """
    filtros = {"alumno_id": alumno.usuario_id}
    if curso:
        filtros["tarea__curso_id"] = curso.id
    calificaciones = Calificacion.objects.filter(**filtros)
    if periodo:
        calificaciones = calificaciones.filter(
            Q(tarea__periodo=periodo)
            | Q(tarea__periodo__isnull=True)
        )
    actividades = CalificacionActividad.objects.filter(alumno_id=alumno.usuario_id)
    if curso:
        actividades = actividades.filter(actividad__curso_id=curso.id)
    if periodo:
        actividades = actividades.filter(
            Q(actividad__periodo=periodo)
            | Q(actividad__periodo__isnull=True)
        )
    return calcular_promedio_calificaciones(list(calificaciones) + list(actividades))


def obtener_libro_calificaciones(asignacion, periodo=None):
    """
    Construye el libro de calificaciones utilizando
    las mismas Calificacion creadas desde Tareas.

    AsignacionDocente ahora está relacionada directamente
    con Curso y ya no tiene el campo clase.

    Este servicio NO crea calificaciones.
    """

    # =========================================================
    # CURSO DE LA ASIGNACIÓN
    # =========================================================

    curso = asignacion.curso

    if not curso:
        return [], [], []

    # =========================================================
    # ALUMNOS DEL CURSO
    # =========================================================

    alumnos = list(
        Alumnos.objects
        .filter(
            curso_id=curso.id,
            activo=True,
        )
        .select_related(
            "usuario"
        )
        .order_by(
            "usuario__last_name",
            "usuario__first_name",
        )
    )

    # =========================================================
    # TAREAS DEL DOCENTE Y DEL CURSO
    # =========================================================

    tareas = list(_obtener_tareas_asignacion(asignacion, periodo))
    actividades = list(_obtener_actividades_asignacion(asignacion, periodo))

    # =========================================================
    # SI NO HAY ALUMNOS O TAREAS
    # =========================================================

    if not alumnos:
        return alumnos, tareas, actividades

    # =========================================================
    # IDs
    # =========================================================

    alumno_ids = [
        alumno.usuario_id
        for alumno in alumnos
    ]

    tarea_ids = [tarea.id for tarea in tareas]
    actividad_ids = [actividad.id for actividad in actividades]

    # =========================================================
    # CALIFICACIONES EXISTENTES
    # =========================================================

    calificaciones = Calificacion.objects.filter(alumno_id__in=alumno_ids, tarea_id__in=tarea_ids)
    calificaciones_actividades = CalificacionActividad.objects.filter(
        alumno_id__in=alumno_ids, actividad_id__in=actividad_ids,
    )

    # =========================================================
    # DICCIONARIO DE CALIFICACIONES
    # =========================================================

    calificaciones_dict = {
        (
            calificacion.alumno_id,
            calificacion.tarea_id
        ): calificacion
        for calificacion in calificaciones
    }
    calificaciones_actividades_dict = {
        (calificacion.alumno_id, calificacion.actividad_id): calificacion
        for calificacion in calificaciones_actividades
    }

    # =========================================================
    # CONSTRUIR FILAS
    # =========================================================

    for alumno in alumnos:

        fila_notas = []
        notas_existentes = []

        for tarea in tareas:

            calificacion = calificaciones_dict.get(
                (
                    alumno.usuario_id,
                    tarea.id
                )
            )

            if calificacion:

                nota = calificacion.nota

                notas_existentes.append(
                    Decimal(str(nota))
                )

            else:

                nota = None

            fila_notas.append({
                "tarea": tarea,
                "nota": nota,
                "calificacion": calificacion,
            })

        alumno.fila_notas = fila_notas

        alumno.fila_actividades = []
        for actividad in actividades:
            calificacion = calificaciones_actividades_dict.get((alumno.usuario_id, actividad.id))
            alumno.fila_actividades.append({
                "actividad": actividad,
                "nota": calificacion.nota if calificacion else None,
                "calificacion": calificacion,
            })

        # =====================================================
        # PROMEDIO
        # =====================================================

        registros = [fila["calificacion"] for fila in fila_notas if fila["calificacion"]]
        registros += [fila["calificacion"] for fila in alumno.fila_actividades if fila["calificacion"]]
        alumno.promedio = calcular_promedio_calificaciones(registros)

        # =====================================================
        # TAREAS CALIFICADAS
        # =====================================================

        alumno.tareas_calificadas = len(
            notas_existentes
        )

        # =====================================================
        # TAREAS PENDIENTES
        # =====================================================

        alumno.tareas_pendientes = (
            len(tareas) + len(actividades)
            - len(notas_existentes)
            - len([fila for fila in alumno.fila_actividades if fila["nota"] is not None])
        )

        # =====================================================
        # ESTADO ACADÉMICO
        # =====================================================

        if alumno.promedio is None:

            alumno.estado_academico = (
                "Sin calificaciones"
            )

        elif alumno.promedio >= Decimal("4.5"):

            alumno.estado_academico = "Superior"

        elif alumno.promedio >= Decimal("4.0"):

            alumno.estado_academico = "Alto"

        elif alumno.promedio >= Decimal("3.0"):

            alumno.estado_academico = "Básico"

        else:

            alumno.estado_academico = "Bajo"

        # =====================================================
        # ESTUDIANTE EN RIESGO
        # =====================================================

        alumno.en_riesgo = (
            alumno.promedio is not None
            and alumno.promedio < Decimal("3.0")
        )

    return alumnos, tareas, actividades
