from apps.alumnos.models import Alumnos


def obtener_alumnos():
    return Alumnos.objects.select_related(
        "usuario",
        "curso"
    ).all()