from apps.alumnos.models import Alumnos
from apps.cursos.models import Cursos
from apps.clases.models import Clases
from apps.docentes.models import Docente
from apps.tareas.models import Tareas, Calificacion
from apps.asistencia.models import Asistencia

def obtener_asistencia_por_curso_fecha(curso_id, fecha):
    return Asistencia.objects.filter(curso_id=curso_id, fecha=fecha)

def obtener_tareas_docente(clase_id, curso_id):
    return Tareas.objects.filter(clase_id=clase_id, curso_id=curso_id).order_by("fecha_creacion")

def obtener_calificaciones_por_tareas(tarea_ids):
    return Calificacion.objects.filter(tarea_id__in=tarea_ids)

def obtener_alumnos_por_curso(curso_id):
    return Alumnos.objects.filter(
        curso_id=curso_id
    ).select_related(
        "usuario",
        "curso",
        "clase"
    )

def alumnos_totales():
    return Alumnos.objects.all().select_related(
        "usuario",
        "curso",
        "clase"
    )

def obtener_curso(curso_id):
    return Cursos.objects.filter(id=curso_id).first()

def obtener_alumnos_por_curso(curso_id):
    return Alumnos.objects.filter(
        curso_id=curso_id
    ).select_related(
        "usuario",
        "curso",
        "clase"
    )


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

def obtener_alumnos_por_curso(curso_id):
    return Alumnos.objects.select_related(
        "usuario",
        "curso",
        "clase",
    ).filter(
        curso_id=curso_id,
        activo=True,
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