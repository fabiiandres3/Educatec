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

        pregunta = get_object_or_404(Pregunta, tarea=tarea, descripcion=enunciado)

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
            opcion_id = request.POST.get(f"opcion_seleccionada_{indice}")

            if opcion_id:
                opcion = get_object_or_404(OpcionesRespuesta, id=opcion_id)

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

    # Guardar la nota final
    nota = calcular_nota_final(request.user, tarea)

    calificacion, creada = Calificacion.objects.get_or_create(
        alumno=request.user,
        tarea=tarea,
        defaults={"nota": nota},
    )


def calcular_nota_final(alumno, tarea):
    respuestas = RespuestaAlumno.objects.filter(alumno=alumno, pregunta__tarea=tarea)

    if not respuestas.exists():
        return 0.0

    # Si hay preguntas abiertas sin calificar, no mostrar nota aún
    if respuestas.filter(pregunta__tipo="texto", calificada=False).exists():
        return 0.0

    puntos_obtenidos = respuestas.aggregate(total=Sum("nota_obtenida"))["total"] or 0

    puntos_totales = tarea.preguntas.aggregate(total=Sum("puntaje"))["total"] or 0

    if puntos_totales == 0:
        return 0.0

    nota = (float(puntos_obtenidos) / float(puntos_totales)) * 4 + 1

    return round(nota, 2)
