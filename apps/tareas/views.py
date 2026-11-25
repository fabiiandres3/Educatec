from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mass_mail
from apps.user.decorators import rol_requerido
import logging

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
from apps.alumnos.models import Alumnos
from apps.user.models import Notificacion


logger = logging.getLogger(__name__)


def notificar_alumnos_nueva_tarea(request, tarea):
    """Send a private email notice to active students enrolled in the task course."""
    if not tarea.curso:
        return 0, "La tarea se creó, pero no se eligió un curso para notificar."

    alumnos = Alumnos.objects.filter(
        curso=tarea.curso,
        activo=True,
        usuario__is_active=True,
        usuario__rol__nombre__iexact="alumno",
    ).select_related("usuario")

    correos_vistos = set()
    destinatarios = []
    avisos = []
    for alumno in alumnos:
        fecha = tarea.fecha_entrega.strftime("%d/%m/%Y") if tarea.fecha_entrega else "Sin fecha límite"
        avisos.append(Notificacion(
            usuario=alumno.usuario,
            titulo="Nueva tarea asignada",
            mensaje=f"{tarea.titulo} fue asignada a {tarea.curso.nombre}. Fecha de entrega: {fecha}.",
            url=reverse("listar_tareas_alumno"),
            tipo="tarea",
        ))
        correo = (alumno.usuario.email or "").strip().lower()
        if correo and correo not in correos_vistos:
            correos_vistos.add(correo)
            destinatarios.append((alumno.usuario.first_name or alumno.usuario.username, correo))

    if avisos:
        Notificacion.objects.bulk_create(avisos)

    if not destinatarios:
        return 0, f"La tarea se creó, pero no hay alumnos activos con correo en {tarea.curso.nombre}."

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return 0, "La tarea se creó, pero el servicio de correo no está configurado."

    fecha_entrega = tarea.fecha_entrega.strftime("%d/%m/%Y") if tarea.fecha_entrega else "Sin fecha límite"
    enlace = request.build_absolute_uri(reverse("login"))
    asunto = f"Nueva tarea: {tarea.titulo}"
    mensajes = []
    for nombre, correo in destinatarios:
        cuerpo = (
            f"Hola {nombre},\n\n"
            f"Se asignó una nueva tarea para tu curso {tarea.curso.nombre}.\n\n"
            f"Tarea: {tarea.titulo}\n"
            f"Materia: {tarea.clase or 'Sin materia'}\n"
            f"Fecha de entrega: {fecha_entrega}\n\n"
            f"{tarea.descripcion or ''}\n\n"
            f"Ingresa a Educatec para revisar la actividad: {enlace}\n"
        )
        mensajes.append((asunto, cuerpo, settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER, [correo]))

    try:
        enviados = send_mass_mail(tuple(mensajes), fail_silently=False)
    except Exception:
        logger.exception("No se pudieron enviar las notificaciones de la tarea %s", tarea.pk)
        return 0, "La tarea se creó, pero ocurrió un error al enviar los correos."

    return enviados, None


def notificar_alumno_tarea(request, tarea, alumno):
    """Notify one student when a teacher re-enables an individual task."""
    url = request.build_absolute_uri(reverse("listar_tareas_alumno"))
    fecha = tarea.fecha_entrega.strftime("%d/%m/%Y") if tarea.fecha_entrega else "Sin fecha límite"
    Notificacion.objects.create(
        usuario=alumno,
        titulo="Tarea habilitada nuevamente",
        mensaje=f"{tarea.titulo} está disponible. Fecha de entrega: {fecha}.",
        url=url,
        tipo="tarea",
    )
    if not alumno.email or not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return False
    asunto = f"Tarea disponible en Educatec: {tarea.titulo}"
    cuerpo = (
        f"Hola {alumno.first_name or alumno.username},\n\n"
        f"La tarea {tarea.titulo} está disponible nuevamente.\n"
        f"Curso: {tarea.curso or 'Tu curso'}\nFecha de entrega: {fecha}\n\n"
        f"Ingresa a Educatec: {url}"
    )
    try:
        return send_mass_mail(((
            asunto,
            cuerpo,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [alumno.email],
        ),), fail_silently=False) > 0
    except Exception:
        logger.exception("No se pudo notificar la tarea %s al alumno %s", tarea.pk, alumno.pk)
        return False


# ============================================================
# LISTAR TAREAS
# ============================================================

@rol_requerido("administrador")
def Listar_tareas(request):

    tareas = Tareas.objects.select_related(
        "clase", "curso", "docente__usuario"
    ).prefetch_related("imagenes").all()
    for tarea in tareas:
        tarea.imagenes_lista = [
            imagen for imagen in tarea.imagenes.all() if imagen.imagen
        ]

    return render(
        request,
        "admin/tareas/tareas.html",
        {
            "tareas": tareas,
            "tareas_activas": tareas.filter(activa=True).count(),
            "tareas_inactivas": tareas.filter(activa=False).count(),
        }
    )


# ============================================================
# CREAR TAREA
# ============================================================

@rol_requerido("administrador")
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

            enviados, aviso_correo = notificar_alumnos_nueva_tarea(request, tarea)
            if enviados:
                messages.success(
                    request,
                    f"Tarea creada. Se envió un aviso por correo a {enviados} alumno(s) de {tarea.curso.nombre}.",
                )
            else:
                messages.success(request, "La tarea se creó correctamente.")
            if aviso_correo:
                messages.warning(request, aviso_correo)

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

@rol_requerido("administrador")
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
            with transaction.atomic():
                tarea = tarea_form.save()

                Imagen.objects.filter(
                    tarea=tarea,
                    id__in=request.POST.getlist("eliminar_imagenes"),
                ).delete()
                ArchivoTarea.objects.filter(
                    tarea=tarea,
                    id__in=request.POST.getlist("eliminar_archivos"),
                ).delete()
                tarea.video_set.filter(
                    id__in=request.POST.getlist("eliminar_videos"),
                ).delete()

                for imagen in request.FILES.getlist("imagenes"):
                    Imagen.objects.create(tarea=tarea, imagen=imagen)
                for archivo in request.FILES.getlist("archivos"):
                    ArchivoTarea.objects.create(tarea=tarea, archivo=archivo)
                for video in request.POST.getlist("videos"):
                    if video.strip():
                        Video.objects.create(tarea=tarea, video=video.strip())

                Crear_preguntas(request, tarea)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                messages.success(request, "¡Listo! Los cambios de la tarea se guardaron correctamente.")
                return JsonResponse({
                    "success": True,
                    "message": "¡Cambios guardados! La tarea ya está actualizada.",
                    "redirect_url": reverse("listar_tareas"),
                    "imagenes": [
                        {"id": item.pk, "url": item.imagen.url, "name": item.imagen.name.rsplit("/", 1)[-1]}
                        for item in tarea.imagenes.all() if item.imagen
                    ],
                    "archivos": [
                        {"id": item.pk, "name": item.archivo.name.rsplit("/", 1)[-1], "url": item.archivo.url}
                        for item in tarea.archivos.all() if item.archivo
                    ],
                    "videos": [
                        {"id": item.pk, "url": str(item.video)}
                        for item in tarea.video_set.all()
                    ],
                })

            return redirect(
                "listar_tareas"
            )
        elif request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "errors": tarea_form.errors.get_json_data(),
            }, status=400)

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
            "video_url_nuevo": request.POST.get("videos", "") if request.method == "POST" else "",
        },
    )


# ============================================================
# ELIMINAR TAREA
# ============================================================

@rol_requerido("administrador")
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

@rol_requerido("administrador")
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

@rol_requerido("docente")
def Ver_respuesta(request, tarea_id, alumno_id):

    # ========================================================
    # OBTENER TAREA
    # ========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente__usuario=request.user,
    )

    # ========================================================
    # OBTENER ALUMNO
    # ========================================================

    from apps.user.models import Usuario

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )
    get_object_or_404(
        RespuestaAlumno,
        alumno=alumno,
        pregunta__tarea=tarea,
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

@rol_requerido("docente")
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
