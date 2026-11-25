from django.db.models import Count

from apps.alumnos.models import Alumnos
from apps.cursos.models import Cursos
from apps.clases.models import Clases
from apps.docentes.models import Docente
from apps.tareas.models import Tareas, Calificacion, RespuestaAlumno
from apps.asistencia.models import Asistencia


def obtener_resumen_tareas_por_alumno(alumnos):
    """Resume las tareas activas con la misma regla que usa el listado del alumno."""
    alumnos = list(alumnos)
    resumen = {
        alumno.id: {"total": 0, "entregadas": 0, "pendientes": 0}
        for alumno in alumnos
    }
    cursos_ids = {alumno.curso_id for alumno in alumnos if alumno.curso_id}
    usuarios_ids = {alumno.usuario_id for alumno in alumnos}
    if not cursos_ids or not usuarios_ids:
        return resumen

    tareas = list(
        Tareas.objects.filter(curso_id__in=cursos_ids, activa=True)
        .annotate(total_preguntas=Count("preguntas", distinct=True))
        .values("id", "curso_id", "total_preguntas")
    )
    if not tareas:
        return resumen

    tareas_por_curso = {}
    for tarea in tareas:
        tareas_por_curso.setdefault(tarea["curso_id"], []).append(tarea)

    respuestas_por_usuario_tarea = {
        (fila["alumno_id"], fila["pregunta__tarea_id"]): fila["total"]
        for fila in RespuestaAlumno.objects.filter(
            alumno_id__in=usuarios_ids,
            pregunta__tarea_id__in=[tarea["id"] for tarea in tareas],
        )
        .values("alumno_id", "pregunta__tarea_id")
        .annotate(total=Count("pregunta_id", distinct=True))
    }

    for alumno in alumnos:
        tareas_alumno = tareas_por_curso.get(alumno.curso_id, [])
        entregadas = sum(
            1
            for tarea in tareas_alumno
            if tarea["total_preguntas"] > 0
            and respuestas_por_usuario_tarea.get((alumno.usuario_id, tarea["id"]), 0)
            >= tarea["total_preguntas"]
        )
        total = len(tareas_alumno)
        resumen[alumno.id] = {
            "total": total,
            "entregadas": entregadas,
            "pendientes": total - entregadas,
        }
    return resumen

def obtener_asistencia_por_curso_fecha(curso_id, fecha):
    return Asistencia.objects.filter(
        curso_id=curso_id,
        fecha=fecha
    )

def obtener_tareas_docente(clase_id, curso_id):
    return Tareas.objects.filter(clase_id=clase_id, curso_id=curso_id).order_by("fecha_creacion")

def obtener_calificaciones_por_tareas(tarea_ids):
    return Calificacion.objects.filter(tarea_id__in=tarea_ids)

def obtener_alumnos_por_curso(curso_id):
    return Alumnos.objects.select_related(
        "usuario",
        "curso",
        "clase",
    ).filter(
        curso_id=curso_id,
        activo=True,
    )

def alumnos_totales():
    return Alumnos.objects.all().select_related(
        "usuario",
        "curso",
        "clase"
    )

def obtener_curso(curso_id):
    return Cursos.objects.filter(id=curso_id).first()



def contar_materias():
    return Clases.objects.count()

def contar_alumnos():
    return Alumnos.objects.count()

def contar_alumnos_curso(curso_id):
    return Alumnos.objects.filter(curso_id=curso_id).count()

def obtener_docente():
    return Docente.objects.values(
        'usuario__username'
    )

def obtener_cursos():
    return Cursos.objects.all()

def obtener_materias():
    return Clases.objects.all()

def obtener_alumnos_asistencia():
    return Alumnos.objects.values(
        'clase__titulo',
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'curso__nombre',
    )




def contar_alumnos_curso(curso_id):
    return Alumnos.objects.filter(
        curso_id=curso_id,
        activo=True,
    ).count()


def obtener_tareas_docente(clase_id, curso_id):
    return Tareas.objects.filter(
        clase_id=clase_id,
        curso_id=curso_id,
    ).order_by(
        "fecha_entrega",
        "titulo",
    )
