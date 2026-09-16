from .models import Pregunta, OpcionesRespuesta, RespuestaCorrecta, RespuestaAlumno
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import Calificacion


def Crear_preguntas(request, tarea):

    indice = 0

    while True:
        enunciado = request.POST.get(f"pregunta_{indice}")

        if enunciado is None:
            break

        tipo = request.POST.get(f"tipo_{indice}")
        puntaje = request.POST.get(f"puntaje_{indice}")

        pregunta = Pregunta.objects.create(  # le asignamos los valores a los campos de la model Pregunta [tarea(FK), descripcion, tipo, puntaje]
            tarea=tarea, descripcion=enunciado, tipo=tipo, puntaje=puntaje
        )

        if tipo == "texto":
            respuesta = request.POST.get(f"respuesta_correcta_{indice}")
            if respuesta:
                RespuestaCorrecta.objects.create(pregunta=pregunta, respuesta=respuesta)

        elif tipo == "opcion":
            opciones = request.POST.getlist(f"opciones_{indice}[]")

            correcta = request.POST.get(f"correcta_{indice}")

            letras = ["A", "B", "C", "D"]

            for i, opcion in enumerate(opciones):
                if opcion.strip():
                    OpcionesRespuesta.objects.create(
                        pregunta=pregunta,
                        opcion=opcion,
                        es_correcta=(letras[i] == correcta),
                    )

        indice += 1


def Respuesta_alumno(request, tarea):

    indice = 0

    while True:
        enunciado = request.POST.get(f"pregunta_{indice}")

        if enunciado is None:
            break

        tipo = request.POST.get(f"tipo_{indice}")

        pregunta = get_object_or_404(
            Pregunta,
            tarea=tarea,
            descripcion=enunciado
        )

        if tipo == "texto":

            respuesta_texto = request.POST.get(f"respuesta_{indice}")

            if respuesta_texto:

                RespuestaAlumno.objects.create(
                    alumno=request.user,
                    pregunta=pregunta,
                    respuesta_texto=respuesta_texto,
                    nota_obtenida=0,
                )

        elif tipo == "opcion":

            opcion_id = request.POST.get(
                f"opcion_seleccionada_{indice}"
            )

            if opcion_id:

                opcion = get_object_or_404(
                    OpcionesRespuesta,
                    id=opcion_id
                )

                respuesta = RespuestaAlumno.objects.create(
                    alumno=request.user,
                    pregunta=pregunta,
                    opcion_seleccionada=opcion,
                    es_correcta=opcion.es_correcta,
                    nota_obtenida=0,
                )

                if opcion.es_correcta:
                    respuesta.nota_obtenida = pregunta.puntaje
                else:
                    respuesta.nota_obtenida = 0

                respuesta.save()

        indice += 1

    # =========================================================
    # CALCULAR Y GUARDAR LA CALIFICACIÓN FINAL
    # =========================================================

    nota = calcular_nota_final(
        request.user,
        tarea
    )

    # IMPORTANTE:
    # Si ya existe la calificación, la actualiza.
    # Si no existe, la crea.

    Calificacion.objects.update_or_create(
        alumno=request.user,
        tarea=tarea,
        defaults={
            "nota": nota
        }
    )


def calcular_nota_final(alumno, tarea):

    respuestas = RespuestaAlumno.objects.filter(
        alumno=alumno,
        pregunta__tarea=tarea
    )

    # ---------------------------------------------------------
    # SI NO HAY RESPUESTAS
    # ---------------------------------------------------------

    if not respuestas.exists():
        return 0.0


    # ---------------------------------------------------------
    # SI HAY PREGUNTAS DE TEXTO SIN CALIFICAR
    # ---------------------------------------------------------

    if respuestas.filter(
        pregunta__tipo="texto",
        calificada=False
    ).exists():

        return 0.0


    # ---------------------------------------------------------
    # PUNTOS OBTENIDOS
    # ---------------------------------------------------------

    puntos_obtenidos = respuestas.aggregate(
        total=Sum("nota_obtenida")
    )["total"] or 0


    # ---------------------------------------------------------
    # PUNTOS TOTALES DE LA TAREA
    # ---------------------------------------------------------

    puntos_totales = tarea.preguntas.aggregate(
        total=Sum("puntaje")
    )["total"] or 0


    # ---------------------------------------------------------
    # EVITAR DIVISIÓN POR CERO
    # ---------------------------------------------------------

    if puntos_totales == 0:
        return 0.0


    # ---------------------------------------------------------
    # CONVERTIR DIRECTAMENTE A ESCALA 0.0 - 5.0
    # ---------------------------------------------------------

    nota = (
        float(puntos_obtenidos)
        / float(puntos_totales)
    ) * 5


    # ---------------------------------------------------------
    # REDONDEAR A DOS DECIMALES
    # ---------------------------------------------------------

    return round(nota, 2)