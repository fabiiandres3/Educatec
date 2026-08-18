from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from apps.user.models import Usuario
from apps.alumnos.models import Alumnos
from apps.user.forms import EditarUsuarioForm
from apps.alumnos.forms import AlumnoForm
from apps.tareas.models import (
    Tareas,
    Imagen,
    ArchivoTarea,
    Video,
    Pregunta,
    RespuestaAlumno,
    Calificacion,
    OpcionesRespuesta,
    RespuestaCorrecta,
)

from apps.tareas.forms import TareasForm
from apps.tareas.services import Crear_preguntas

# Create your views here.


def Listar_alumnos(request):
    alumnos = Usuario.objects.filter(rol__nombre='alumno')

    return render(request, 'admin/alumnos/alumnos.html', {'alumnos':alumnos})


def Editar_alumno(request, alumno_id):

    alumno = get_object_or_404(
        Alumnos,
        usuario_id=alumno_id
    )

    usuario = alumno.usuario

    if request.method == "POST":

        usuario_form = EditarUsuarioForm(
            request.POST,
            instance=usuario
        )

        alumno_form = AlumnoForm(
            request.POST,
            instance=alumno
        )

        if usuario_form.is_valid() and alumno_form.is_valid():

            nuevo_curso = alumno_form.cleaned_data.get("curso")

            # Verificar si se está asignando un curso
            if nuevo_curso:

                cantidad_alumnos = Alumnos.objects.filter(
                    curso=nuevo_curso
                ).exclude(
                    pk=alumno.pk
                ).count()

                if cantidad_alumnos >= 3:

                    messages.error(
                        request,
                        f"El curso {nuevo_curso.nombre} ya alcanzó "
                        "el límite máximo de 32 alumnos."
                    )

                    return render(
                        request,
                        "admin/alumnos/editar_alumno.html",
                        {
                            "usuario_form": usuario_form,
                            "alumno_form": alumno_form,
                        },
                    )

            usuario_form.save()
            alumno_form.save()

            messages.success(
                request,
                "Alumno actualizado correctamente."
            )

            return redirect("listar_alumnos")

    else:

        usuario_form = EditarUsuarioForm(
            instance=usuario
        )

        alumno_form = AlumnoForm(
            instance=alumno
        )

    return render(
        request,
        "admin/alumnos/editar_alumno.html",
        {
            "usuario_form": usuario_form,
            "alumno_form": alumno_form,
        },
    )


def Eliminar_alumno(request, docente_id):
    alumno = get_object_or_404(Alumnos, usuario_id=docente_id)

    if request.method == "POST":
        alumno.usuario.delete()  # Elimina Usuario y Docente si la relación es CASCADE
        return redirect("listar_alumnos")

    return render(
        request,
        "admin/alumnos/eliminar_alumno.html",
        {
            "alumno": alumno,
        },
    )



def listar_tareas_alumno(request):

    alumno = get_object_or_404(
        Alumnos,
        usuario=request.user
    )

    curso = alumno.curso

    if not curso:
        messages.error(
            request,
            "No tienes un curso asignado."
        )

        return redirect("dashboard_alumnos")

    tareas = (
        Tareas.objects
        .filter(curso=curso)
        .select_related("curso", "clase")
        .order_by("-fecha_creacion")
    )

    return render(
        request,
        "paneles/alumnos/tareas/listar_tareas_alumno.html",
        {
            "alumno": alumno,
            "curso": curso,
            "tareas": tareas,
        }
    )


def responder_tarea(request, tarea_id):
    tarea = get_object_or_404(Tareas, id=tarea_id)

    alumno = get_object_or_404(
        Alumnos,
        usuario=request.user
    )

    preguntas = tarea.preguntas.prefetch_related(
        "opciones"
    ).all()

    if request.method == "POST":

        pregunta_id = request.POST.get("pregunta_id")

        pregunta = get_object_or_404(
            Pregunta,
            id=pregunta_id,
            tarea=tarea
        )

        # Evitar que el alumno responda nuevamente
        respuesta_existente = RespuestaAlumno.objects.filter(
            alumno=request.user,
            pregunta=pregunta
        ).first()

        if respuesta_existente:
            messages.warning(
                request,
                "Ya has respondido esta pregunta."
            )

            return redirect(
                "responder_tarea_alumno",
                tarea_id=tarea.id
            )

        respuesta = RespuestaAlumno(
            alumno=request.user,
            pregunta=pregunta
        )

        if pregunta.tipo == "texto":

            respuesta_texto = request.POST.get(
                "respuesta_texto",
                ""
            ).strip()

            if not respuesta_texto:
                messages.error(
                    request,
                    "Debes escribir una respuesta."
                )

                return redirect(
                    "responder_tarea_alumno",
                    tarea_id=tarea.id
                )

            respuesta.respuesta_texto = respuesta_texto

        elif pregunta.tipo == "opcion":

            opcion_id = request.POST.get(
                "opcion_seleccionada"
            )

            if not opcion_id:
                messages.error(
                    request,
                    "Debes seleccionar una opción."
                )

                return redirect(
                    "responder_tarea_alumno",
                    tarea_id=tarea.id
                )

            opcion = get_object_or_404(
                OpcionesRespuesta,
                id=opcion_id,
                pregunta=pregunta
            )

            respuesta.opcion_seleccionada = opcion

            # Las preguntas de opción se pueden
            # calificar automáticamente.
            respuesta.es_correcta = opcion.es_correcta
            respuesta.nota_obtenida = (
                pregunta.puntaje
                if opcion.es_correcta
                else 0
            )
            respuesta.calificada = True

        respuesta.save()

        messages.success(
            request,
            "Respuesta enviada correctamente."
        )

        return redirect(
            "responder_tarea_alumno",
            tarea_id=tarea.id
        )

    # =====================================================
    # PREPARAR LAS PREGUNTAS CON SU RESPUESTA
    # =====================================================

    preguntas_data = []

    for pregunta in preguntas:

        respuesta = RespuestaAlumno.objects.filter(
            alumno=request.user,
            pregunta=pregunta
        ).first()

        preguntas_data.append({
            "pregunta": pregunta,
            "respuesta": respuesta,
        })

    return render(
        request,
        "paneles/alumnos/tareas/responder_tarea_alumno.html",
        {
            "tarea": tarea,
            "alumno": alumno,
            "preguntas": preguntas_data,
        }
    )

def respuesta_alumnos(request, tarea_id):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # Verificar que el docente tenga acceso
    if docente.curso not in tarea.cursos.all():
        messages.error(
            request,
            "No tienes permiso para ver esta tarea."
        )

        return redirect("listar_tareas_docentes")

    # Obtener alumnos que respondieron
    alumnos_ids = (
        RespuestaAlumno.objects
        .filter(
            pregunta__tarea=tarea
        )
        .values_list(
            "alumno_id",
            flat=True
        )
        .distinct()
    )

    alumnos = Usuario.objects.filter(
        id__in=alumnos_ids
    )

    return render(
        request,
        "paneles/docentes/tareas/respuesta_alumnos.html",
        {
            "tarea": tarea,
            "alumnos": alumnos,
        }
    )