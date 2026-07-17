from apps.alumnos.models import Alumnos


def obtener_alumnos_asistencia():
    return Alumnos.objects.values(
        'clase__titulo',
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'curso__nombre',
    )