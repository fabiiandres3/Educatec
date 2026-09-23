from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Tareas,
    Imagen,
    ArchivoTarea,
    Video,
    RespuestaAlumno,
    Calificacion,
)

from .forms import TareasForm

from .services import (
    Crear_preguntas,
    Respuesta_alumno,
    calcular_nota_final,
)

from apps.eventos.models import Evento
from apps.docentes.models import Docente


# ============================================================
# LISTAR TAREAS
# ============================================================

def Listar_tareas(request):

    tareas = Tareas.objects.all()

    return render(
        request,
        "admin/tareas/tareas.html",
        {
            "tareas": tareas
        }
    )


# ============================================================
# CREAR TAREA
# ============================================================

def Crear_tarea(request):

    eventos = Evento.objects.filter(
        publicado=True
    ).order_by("fecha", "hora_inicio")

    if request.method == "POST":

        tarea_form = TareasForm(
            request.POST,
            request.FILES
        )

        if tarea_form.is_valid():

            tarea = tarea_form.save()

            # ------------------------------------------------
            # IMÁGENES
            # ------------------------------------------------

            imagenes = request.FILES.getlist(
                "imagenes"
            )

            for imagen in imagenes:

                Imagen.objects.create(
                    tarea=tarea,
                    imagen=imagen
                )

            # ------------------------------------------------
            # ARCHIVOS
            # ------------------------------------------------

            archivos = request.FILES.getlist(
                "archivos"
            )

            for archivo in archivos:

                ArchivoTarea.objects.create(
                    tarea=tarea,
                    archivo=archivo
                )

            # ------------------------------------------------
            # VIDEOS
            # ------------------------------------------------

            videos = request.POST.getlist(
                "videos"
            )

            for video in videos:

                if video.strip():

                    Video.objects.create(
                        tarea=tarea,
                        video=video
                    )

            # ------------------------------------------------
            # PREGUNTAS
            # ------------------------------------------------

            Crear_preguntas(
                request,
                tarea
            )

            return redirect(
                "listar_tareas"
            )

        else:

            print(tarea_form.errors)

    else:

        tarea_form = TareasForm()

    return render(
        request,
        "admin/tareas/crear_tarea.html",
        {
            "tarea_form": tarea_form,
            "eventos": eventos,
        },
    )


# ============================================================
# EDITAR TAREA
# ============================================================

def Editar_tarea(request, tarea_id):

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    if request.method == "POST":

        tarea_form = TareasForm(
            request.POST,
            request.FILES,
            instance=tarea
        )

        if tarea_form.is_valid():

            tarea = tarea_form.save()

            # ------------------------------------------------
            # ELIMINAR IMÁGENES
            # ------------------------------------------------

            imagenes_eliminar = request.POST.getlist(
                "eliminar_imagenes"
            )

            Imagen.objects.filter(
                id__in=imagenes_eliminar
            ).delete()

            # ------------------------------------------------
            # ELIMINAR ARCHIVOS
            # ------------------------------------------------

            archivos_eliminar = request.POST.getlist(
                "eliminar_archivos"
            )

            ArchivoTarea.objects.filter(
                id__in=archivos_eliminar
            ).delete()

            # ------------------------------------------------
            # ELIMINAR VIDEOS
            # ------------------------------------------------

            videos_eliminar = request.POST.getlist(
                "eliminar_videos"
            )

            Video.objects.filter(
                id__in=videos_eliminar
            ).delete()

            # ------------------------------------------------
            # AGREGAR NUEVOS VIDEOS
            # ------------------------------------------------

            videos = request.POST.getlist(
                "videos"
            )

            for video in videos:

                if video.strip():

                    Video.objects.create(
                        tarea=tarea,
                        video=video
                    )

            return redirect(
                "listar_tareas"
            )

    else:

        tarea_form = TareasForm(
            instance=tarea
        )

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


# ============================================================
# ELIMINAR TAREA
# ============================================================

def Eliminar_tarea(request, tarea_id):

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    tarea.delete()

    return redirect(
        "listar_tareas"
    )


# ============================================================
# DETALLE DE TAREA
# ============================================================

def Detalle_tarea(request, tarea_id):

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # --------------------------------------------------------
    # CUANDO EL ALUMNO ENVÍA LA TAREA
    # --------------------------------------------------------

    if request.method == "POST":

        Respuesta_alumno(
            request,
            tarea
        )

        return redirect(
            "listar_tareas"
        )

    # --------------------------------------------------------
    # PREGUNTAS
    # --------------------------------------------------------

    preguntas = tarea.preguntas.all()

    for pregunta in preguntas:

        pregunta.respondida = (
            RespuestaAlumno.objects.filter(
                alumno=request.user,
                pregunta=pregunta
            ).exists()
        )

    # --------------------------------------------------------
    # BUSCAR CALIFICACIÓN EXISTENTE
    # --------------------------------------------------------

    calificacion = Calificacion.objects.filter(
        alumno=request.user,
        tarea=tarea
    ).order_by("-id").first()

    if calificacion:

        nota = calificacion.nota

    else:

        nota = None

    # --------------------------------------------------------
    # MOSTRAR DETALLE
    # --------------------------------------------------------

    return render(
        request,
        "admin/tareas/detalle_tarea.html",
        {
            "tarea": tarea,
            "preguntas": preguntas,
            "nota": nota,
            "calificacion": calificacion,
        },
    )

# ============================================================
# DOCENTE - VER RESPUESTA DEL ESTUDIANTE
# ============================================================

def Ver_respuesta(request, tarea_id, alumno_id):

    # ========================================================
    # OBTENER TAREA
    # ========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # ========================================================
    # OBTENER ALUMNO
    # ========================================================

    from apps.user.models import Usuario

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    # ========================================================
    # OBTENER PREGUNTAS
    # ========================================================

    preguntas = tarea.preguntas.prefetch_related(
        "opciones"
    ).all()

    # ========================================================
    # OBTENER RESPUESTAS DEL ALUMNO
    # ========================================================

    respuestas = RespuestaAlumno.objects.filter(
        alumno_id=alumno_id,
        pregunta__tarea=tarea
    ).select_related(
        "pregunta",
        "opcion_seleccionada"
    )

    # ========================================================
    # MAPA DE RESPUESTAS
    # ========================================================

    respuestas_map = {
        respuesta.pregunta_id: respuesta
        for respuesta in respuestas
    }

    # ========================================================
    # CREAR LISTA PARA LA PLANTILLA
    # ========================================================

    preguntas_respuestas = []

    for pregunta in preguntas:

        respuesta = respuestas_map.get(
            pregunta.id
        )

        preguntas_respuestas.append({
            "pregunta": pregunta,
            "respuesta": respuesta,
        })

    # ========================================================
    # TOTALES
    # ========================================================

    total_preguntas = preguntas.count()

    total_puntos = Decimal("0")

    for pregunta in preguntas:

        if pregunta.puntaje is not None:

            total_puntos += Decimal(
                str(pregunta.puntaje)
            )

    # ========================================================
    # PUNTOS OBTENIDOS
    # ========================================================

    puntos_obtenidos = Decimal("0")

    for respuesta in respuestas:

        if respuesta.nota_obtenida is not None:

            puntos_obtenidos += Decimal(
                str(respuesta.nota_obtenida)
            )

    # ========================================================
    # CALIFICACIÓN GUARDADA
    # ========================================================
    #
    # Esta es la nota final que también utiliza
    # el módulo de Calificaciones.
    #
    # ========================================================

    calificacion = Calificacion.objects.filter(
        alumno_id=alumno_id,
        tarea_id=tarea_id
    ).order_by("-id").first()

    if calificacion:

        nota_final = calificacion.nota

    else:

        nota_final = None

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "paneles/docentes/tareas/ver_respuesta.html",
        {
            "tarea": tarea,
            "alumno": alumno,

            "preguntas": preguntas,
            "respuestas": respuestas,
            "respuestas_map": respuestas_map,
            "preguntas_respuestas": preguntas_respuestas,

            "total_preguntas": total_preguntas,

            "puntos_obtenidos": puntos_obtenidos,
            "puntos_totales": total_puntos,

            "nota_final": nota_final,

            "calificacion": calificacion,
        }
    )

# ============================================================
# DOCENTE - EVALUAR RESPUESTA
# ============================================================

@login_required
def Evaluar_respuesta(request, tarea_id):

    # ========================================================
    # SOLO POST
    # ========================================================

    if request.method != "POST":

        return redirect(
            "listar_tareas"
        )

    # ========================================================
    # OBTENER TAREA
    # ========================================================

    docente = get_object_or_404(Docente, usuario=request.user)
    tarea = get_object_or_404(Tareas, id=tarea_id, docente=docente)

    # ========================================================
    # DATOS RECIBIDOS
    # ========================================================

    respuesta_id = request.POST.get(
        "respuesta_id"
    )

    estado = request.POST.get(
        "estado"
    )

    nota = request.POST.get(
        "nota"
    )

    # ========================================================
    # VALIDAR RESPUESTA
    # ========================================================

    if not respuesta_id:

        return redirect(
            "listar_tareas"
        )

    # ========================================================
    # BUSCAR RESPUESTA
    # ========================================================

    respuesta = get_object_or_404(
        RespuestaAlumno.objects.select_related(
            "pregunta",
            "alumno"
        ),
        id=respuesta_id
    )

    # ========================================================
    # VALIDAR QUE LA RESPUESTA PERTENEZCA A LA TAREA
    # ========================================================

    if respuesta.pregunta.tarea_id != tarea.id:

        return redirect(
            "listar_tareas"
        )

    # ========================================================
    # CONVERTIR NOTA
    # ========================================================

    try:

        nota_decimal = Decimal(
            (nota or "0").replace(",", ".")
        )

    except (
        InvalidOperation,
        AttributeError
    ):

        nota_decimal = Decimal("0")

    # ========================================================
    # VALIDAR NOTA MÍNIMA
    # ========================================================

    if nota_decimal < Decimal("0"):

        nota_decimal = Decimal("0")

    # ========================================================
    # VALIDAR NOTA MÁXIMA DE LA PREGUNTA
    # ========================================================

    puntaje_pregunta = Decimal(
        str(respuesta.pregunta.puntaje or 0)
    )

    if nota_decimal > puntaje_pregunta:

        nota_decimal = puntaje_pregunta

    # ========================================================
    # GUARDAR EVALUACIÓN DE LA RESPUESTA
    # ========================================================

    if estado in ("correct", "correcta"):
        respuesta.nota_obtenida = puntaje_pregunta
        respuesta.calificada = True
        respuesta.es_correcta = True
    elif estado in ("incorrect", "incorrecta"):
        # El botón establece cero por defecto, pero el docente puede
        # asignar puntos al corregir manualmente una respuesta.
        respuesta.nota_obtenida = nota_decimal
        respuesta.calificada = True
        respuesta.es_correcta = False
    elif estado in ("partial", "parcial"):
        respuesta.nota_obtenida = nota_decimal
        respuesta.calificada = True
        respuesta.es_correcta = False
    elif estado == "pending":
        respuesta.nota_obtenida = Decimal("0")
        respuesta.calificada = False
        respuesta.es_correcta = False
    else:
        return redirect("ver_respuesta", tarea_id=tarea.id, alumno_id=respuesta.alumno_id)

    respuesta.save()

    # ========================================================
    # CALCULAR NOTA FINAL DE LA TAREA
    # ========================================================

    nota_final_calculada = calcular_nota_final(
        respuesta.alumno,
        tarea
    )

    # ========================================================
    # GUARDAR / ACTUALIZAR CALIFICACIÓN
    # ========================================================
    #
    # Esta es la misma calificación que consulta
    # el módulo de Calificaciones.
    #
    # ========================================================

    calificacion, creada = Calificacion.objects.update_or_create(
        alumno=respuesta.alumno,
        tarea=tarea,
        defaults={
            "nota": nota_final_calculada
        }
    )

    # ========================================================
    # REGRESAR A LA RESPUESTA
    # ========================================================

    return redirect(
        "ver_respuesta",
        tarea_id=tarea.id,
        alumno_id=respuesta.alumno_id
    )
