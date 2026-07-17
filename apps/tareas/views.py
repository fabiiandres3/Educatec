from django.shortcuts import render, redirect, get_object_or_404
from urllib.parse import urlparse, parse_qs
from django.db import transaction
from .models import Tareas, Imagen, ArchivoTarea, Video, RespuestaAlumno, Calificacion
from .forms import TareasForm
from .services import Crear_preguntas, Respuesta_alumno, calcular_nota_final

# Create your views here.


def Listar_tareas(request):
    tareas = Tareas.objects.all()
    return render(request, "admin/tareas/tareas.html", {"tareas": tareas})


def Crear_tarea(request):

    if request.method == "POST":
        tarea_form = TareasForm(request.POST, request.FILES)

        if tarea_form.is_valid():
            tarea = tarea_form.save()

            imagenes = request.FILES.getlist("imagenes")
            archivos = request.FILES.getlist("archivos")
            videos = request.POST.getlist("videos")

            for imagen in imagenes:
                Imagen.objects.create(tarea=tarea, imagen=imagen)

            for archivo in archivos:
                ArchivoTarea.objects.create(tarea=tarea, archivo=archivo)

            for video in videos:
                if video.strip():
                    Video.objects.create(tarea=tarea, video=video)

            Crear_preguntas(request, tarea)

            return redirect("listar_tareas")
        else:
            print(tarea_form.errors)

    else:
        tarea_form = TareasForm()

    return render(request, "admin/tareas/crear_tarea.html", {"tarea_form": tarea_form})


def Editar_tarea(request, tarea_id):

    tarea = get_object_or_404(Tareas, id=tarea_id)

    if request.method == "POST":
        tarea_form = TareasForm(request.POST, instance=tarea)

        if tarea_form.is_valid():
            tarea = tarea_form.save()

            # Eliminar imágenes
            imagenes_eliminar = request.POST.getlist("eliminar_imagenes")

            Imagen.objects.filter(id__in=imagenes_eliminar).delete()

            # Eliminar archivos
            archivos_eliminar = request.POST.getlist("eliminar_archivos")

            ArchivoTarea.objects.filter(id__in=archivos_eliminar).delete()

            # Eliminar videos
            videos_eliminar = request.POST.getlist("eliminar_videos")

            Video.objects.filter(id__in=videos_eliminar).delete()

            # Nuevas imágenes
            imagenes = request.FILES.getlist("imagenes")

            for imagen in imagenes:
                Imagen.objects.create(tarea=tarea, imagen=imagen)

            # Nuevos archivos
            archivos = request.FILES.getlist("archivos")

            for archivo in archivos:
                ArchivoTarea.objects.create(tarea=tarea, archivo=archivo)

            # Nuevas URLs de video
            videos = request.POST.getlist("videos")

            for video in videos:
                if video.strip():
                    Video.objects.create(tarea=tarea, video=video)

            return redirect("listar_tareas")

    else:
        tarea_form = TareasForm(instance=tarea)

    return render(
        request,
        "admin/tareas/editar_tarea.html",
        {
            "tarea": tarea,
            "tarea_form": tarea_form,
            "imagenes": tarea.imagenes.all(),
            "archivos": tarea.archivos.all(),
            "videos": tarea.video_set.all(),
        },
    )


def Eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tareas, id=tarea_id)
    tarea.delete()
    return redirect("listar_tareas")


def Detalle_tarea(request, tarea_id):

    tarea = get_object_or_404(Tareas, id=tarea_id)

    if request.method == "POST":
        Respuesta_alumno(request, tarea)
        return redirect("listar_tareas")

    preguntas = tarea.preguntas.all()

    for pregunta in preguntas:
        pregunta.respondida = RespuestaAlumno.objects.filter(
            alumno=request.user,
            pregunta=pregunta
        ).exists()

    try:
        nota = Calificacion.objects.get(
            alumno=request.user,
            tarea=tarea
        ).nota
    except Calificacion.DoesNotExist:
        nota = 0.0

    return render(
        request,
        "admin/tareas/detalle_tarea.html",
        {
            "tarea": tarea,
            "preguntas": preguntas,
            "nota": nota,
        },
    )