"""Contexto global de Educatec: rol del usuario y nivel educativo.

El nivel educativo se deduce a partir del nombre del curso del alumno porque el
modelo ``Cursos`` no tiene un campo de grado/nivel. No se altera la base de
datos: solo se interpreta la información existente.
"""

import unicodedata

from django.utils import timezone

from apps.alumnos.models import Alumnos


ROLES_ALUMNO = {"alumno", "alumnos", "estudiante", "estudiantes"}


def _normalizar(texto):
    """Minúsculas sin acentos para comparar nombres de curso."""
    if not texto:
        return ""
    base = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in base if not unicodedata.combining(c)).lower().strip()


# Palabras clave por nivel. Se comprueban en orden.
_CLAVES_NIVEL = (
    (
        "preescolar",
        (
            "preescolar", "prescolar", "pre-jardin", "prejardin", "jardin",
            "transicion", "parvulos", "kinder", "maternal", "caminadores",
            "pesebre", "infantil",
        ),
    ),
    (
        "media",
        ("media tecnica", "media academica", "media", "decimo", "undecimo"),
    ),
    (
        "secundaria",
        (
            "secundaria", "bachillerato", "sexto", "septimo", "octavo",
            "noveno",
        ),
    ),
    (
        "primaria",
        (
            "primaria", "primero", "segundo", "tercero", "cuarto", "quinto",
        ),
    ),
)

# Números de grado como texto ("6°", "10-A", "11B") por nivel.
_DIGITOS_NIVEL = {
    "1": "primaria",
    "2": "primaria",
    "3": "primaria",
    "4": "primaria",
    "5": "primaria",
    "6": "secundaria",
    "7": "secundaria",
    "8": "secundaria",
    "9": "secundaria",
    "10": "media",
    "11": "media",
}


def detectar_nivel_educativo(nombre_curso):
    """Devuelve el nivel educativo inferido del nombre del curso."""
    texto = _normalizar(nombre_curso)

    if not texto:
        return "default"

    for nivel, claves in _CLAVES_NIVEL:
        for clave in claves:
            if clave in texto:
                return nivel

    # Grado numérico: se toma el primer número de uno o dos dígitos.
    digitos = ""

    for caracter in texto:
        if caracter.isdigit():
            digitos += caracter
            if len(digitos) == 2:
                break
        elif digitos:
            break

    if digitos:
        if digitos in _DIGITOS_NIVEL:
            return _DIGITOS_NIVEL[digitos]
        if digitos[0] in _DIGITOS_NIVEL:
            return _DIGITOS_NIVEL[digitos[0]]

    return "default"


def contexto_educatec(request):
    """Expone el rol y el nivel educativo a todas las plantillas."""
    usuario = getattr(request, "user", None)
    rol = ""
    nivel = "default"
    curso_actual = None

    if usuario is not None and usuario.is_authenticated:
        rol = (usuario.rol.nombre if usuario.rol else "").lower().strip()
        if rol in ROLES_ALUMNO:
            alumno = (
                Alumnos.objects
                .select_related("curso")
                .filter(usuario=usuario, activo=True)
                .first()
            )
            if alumno and alumno.curso:
                curso_actual = alumno.curso
                nivel = detectar_nivel_educativo(alumno.curso.nombre)

    return {
        "rol_usuario": rol,
        "nivel_educativo": nivel,
        "nivel_curso": curso_actual,
        "saludo": _saludo_segun_hora(),
    }


def _saludo_segun_hora():
    """Saludo cordial acorde a la hora local del usuario."""
    hora = timezone.localtime().hour

    if hora < 12:
        return "Buenos días"
    if hora < 19:
        return "Buenas tardes"
    return "Buenas noches"
