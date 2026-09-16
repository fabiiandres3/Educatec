from decimal import Decimal

from apps.alumnos.models import Alumnos
from apps.docentes.models import AsignacionDocente
from apps.tareas.models import Tareas, Calificacion


def obtener_asignaciones_docente(docente):
    """
    Obtiene las clases/materias asignadas al docente.
    """

    return (
        AsignacionDocente.objects
        .filter(docente=docente)
        .select_related(
            "clase",
            "clase__curso",
        )
        .order_by(
            "clase__curso__nombre",
            "clase__titulo",
        )
    )


def obtener_libro_calificaciones(asignacion):
    """
    Construye el libro de calificaciones utilizando
    las mismas Calificacion creadas desde Tareas.

    Este servicio NO crea calificaciones.
    """

    alumnos = list(
        Alumnos.objects
        .filter(
            curso_id=asignacion.clase.curso_id,
            clase_id=asignacion.clase_id,
            activo=True,
        )
        .select_related("usuario")
        .order_by(
            "usuario__last_name",
            "usuario__first_name",
        )
    )

    tareas = list(
        Tareas.objects
        .filter(
            docente=asignacion.docente,
            curso_id=asignacion.clase.curso_id,
            clase_id=asignacion.clase_id,
            activa=True,
        )
        .order_by(
            "fecha_entrega",
            "titulo",
        )
    )

    if not alumnos or not tareas:
        return alumnos, tareas

    alumno_ids = [alumno.usuario_id for alumno in alumnos]
    tarea_ids = [tarea.id for tarea in tareas]

    calificaciones = Calificacion.objects.filter(
        alumno_id__in=alumno_ids,
        tarea_id__in=tarea_ids,
    )

    # Guardamos el objeto completo de Calificacion
    calificaciones_dict = {
        (calificacion.alumno_id, calificacion.tarea_id): calificacion
        for calificacion in calificaciones
    }

    for alumno in alumnos:

        fila_notas = []
        notas_existentes = []

        for tarea in tareas:

            calificacion = calificaciones_dict.get(
                (alumno.usuario_id, tarea.id)
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

        # Promedio
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

        # Cantidad de tareas calificadas
        alumno.tareas_calificadas = len(
            notas_existentes
        )

        # Cantidad de tareas sin calificar
        alumno.tareas_pendientes = (
            len(tareas) - len(notas_existentes)
        )

        # Estado académico
        if alumno.promedio is None:
            alumno.estado_academico = "Sin calificaciones"

        elif alumno.promedio >= Decimal("4.5"):
            alumno.estado_academico = "Superior"

        elif alumno.promedio >= Decimal("4.0"):
            alumno.estado_academico = "Alto"

        elif alumno.promedio >= Decimal("3.0"):
            alumno.estado_academico = "Básico"

        else:
            alumno.estado_academico = "Bajo"

        # Estudiante en riesgo
        alumno.en_riesgo = (
            alumno.promedio is not None
            and alumno.promedio < Decimal("3.0")
        )

    return alumnos, tareas