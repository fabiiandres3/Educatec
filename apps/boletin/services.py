from decimal import Decimal

from apps.calificaciones.services import (
    obtener_promedio_alumno_asignacion,
    obtener_promedio_general_alumno,
)

from .models import ContenidoPedagogico, ObservacionBoletin


NOTA_APROBACION = Decimal("3.50")  # 70 % de la escala vigente 0.00–5.00


def desempeno(nota):
    if nota is None:
        return "Sin calificaciones"
    if nota >= Decimal("4.50"):
        return "Superior"
    if nota >= Decimal("4.00"):
        return "Alto"
    if nota >= Decimal("3.00"):
        return "Básico"
    return "Bajo"


def construir_boletin(
    alumno, periodo, asignaciones, solo_publicados=False, solo_con_notas=False,
):
    """Consolida exclusivamente calificaciones existentes dentro del período.

    Los promedios proceden de apps.calificaciones.services.
    """
    asignaciones = list(asignaciones.select_related("docente__usuario", "curso", "clase"))
    contenidos = {
        item.asignacion_id: item
        for item in ContenidoPedagogico.objects.filter(
            asignacion__in=asignaciones, periodo=periodo
        ).prefetch_related("observaciones")
    }
    observaciones = {
        item.contenido_id: item
        for item in ObservacionBoletin.objects.filter(
            contenido__in=list(contenidos.values()), alumno=alumno
        )
    }
    # El promedio se obtiene del servicio apps.calificaciones.services.
    # Se conserva el período por el rango de fecha de entrega de la tarea.
    filas = []
    for asignacion in asignaciones:
        # Una asignación solo aporta la materia que tiene realmente vinculada.
        promedio_materia = obtener_promedio_alumno_asignacion(alumno, asignacion, periodo)
        contenido = contenidos.get(asignacion.id)
        observacion = observaciones.get(contenido.id) if contenido else None
        publicado = bool(observacion and observacion.publicado)
        completo = bool(contenido and observacion and observacion.observacion.strip() and publicado)
        if solo_publicados and not publicado:
            continue
        # El boletín personal no debe llenar la tabla con las asignaciones de
        # otros docentes para las que este alumno aún no posee notas.
        if solo_con_notas and promedio_materia is None:
            continue
        filas.append({
            "asignacion": asignacion, "materia": asignacion.clase,
            "docente": asignacion.docente, "nota": promedio_materia,
            "desempeno": desempeno(promedio_materia), "contenido": contenido,
            "observacion": observacion, "completo": completo,
            "publicado": publicado,
        })
    # El consolidado del alumno promedia exclusivamente las materias que el
    # docente ya publicó para ese período.
    notas = [fila["nota"] for fila in filas if fila["nota"] is not None]
    promedio = (
        (sum(notas) / Decimal(len(notas))).quantize(Decimal("0.01"))
        if notas else None
    )
    return filas, promedio
