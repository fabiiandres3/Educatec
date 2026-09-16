from decimal import Decimal

from apps.alumnos.models import Alumnos
from apps.docentes.models import AsignacionDocente
from apps.tareas.models import Tareas, Calificacion


def obtener_asignaciones_docente(docente):
    return (
        AsignacionDocente.objects
        .filter(
            docente=docente
        )
        .select_related(
            "docente",
            "curso"
        )
    )



def obtener_libro_calificaciones(asignacion):
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
        return [], []

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

    tareas = list(
        Tareas.objects
        .filter(
            docente=asignacion.docente,
            curso_id=curso.id,
            activa=True,
        )
        .select_related(
            "clase"
        )
        .order_by(
            "fecha_entrega",
            "titulo",
        )
    )

    # =========================================================
    # SI NO HAY ALUMNOS O TAREAS
    # =========================================================

    if not alumnos or not tareas:
        return alumnos, tareas

    # =========================================================
    # IDs
    # =========================================================

    alumno_ids = [
        alumno.usuario_id
        for alumno in alumnos
    ]

    tarea_ids = [
        tarea.id
        for tarea in tareas
    ]

    # =========================================================
    # CALIFICACIONES EXISTENTES
    # =========================================================

    calificaciones = Calificacion.objects.filter(
        alumno_id__in=alumno_ids,
        tarea_id__in=tarea_ids,
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

        # =====================================================
        # PROMEDIO
        # =====================================================

        if notas_existentes:

            promedio = (
                sum(notas_existentes)
                / Decimal(len(notas_existentes))
            )

            alumno.promedio = promedio.quantize(
                Decimal("0.01")
            )

        else:

            alumno.promedio = None

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
            len(tareas)
            - len(notas_existentes)
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

    return alumnos, tareas