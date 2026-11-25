import logging

from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from .forms import EventoForm
from .models import Evento
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _schedule_image_delete(image_field, evento_id):
    """Delete an old object after the database change commits."""
    if not image_field or not image_field.name:
        return

    storage = image_field.storage
    image_name = image_field.name

    def delete_image():
        try:
            storage.delete(image_name)
        except Exception:
            logger.exception(
                "Could not delete event image after database update (event_id=%s, object=%s)",
                evento_id,
                image_name,
            )

    transaction.on_commit(delete_image)


def _image_save_error(evento_id):
    logger.exception("Event save or image upload failed (event_id=%s)", evento_id)
    return JsonResponse({
        "success": False,
        "type": "error",
        "message": "No se pudo guardar la imagen del evento. Revisa la configuración de almacenamiento e inténtalo de nuevo.",
    }, status=500)


# ============================================================
# LISTAR EVENTOS - ADMIN
# ============================================================

def listar_eventos(request):

    eventos = (
        Evento.objects
        .all()
        .order_by(
            "fecha",
            "hora_inicio"
        )
    )

    return render(
        request,
        "admin/eventos/listar_eventos.html",
        {
            "eventos": eventos,
            "eventos_publicados": eventos.filter(publicado=True).count(),
            "eventos_no_publicados": eventos.filter(publicado=False).count(),
        }
    )


# ============================================================
# CREAR EVENTO
# ============================================================

def crear_evento(request):

    # =========================================================
    # MOSTRAR FORMULARIO
    # =========================================================

    if request.method == "GET":

        form = EventoForm()

        return render(
            request,
            "admin/eventos/form_evento.html",
            {
                "form": form,
            }
        )

    # =========================================================
    # PROCESAR FORMULARIO
    # =========================================================

    if request.method == "POST":

        form = EventoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            try:
                evento = form.save()
            except Exception:
                return _image_save_error(None)

            return JsonResponse({
                "success": True,
                "type": "success",
                "message": (
                    f"El evento '{evento.titulo}' "
                    "se creó correctamente."
                )
            })

        # =====================================================
        # ERRORES DEL FORMULARIO
        # =====================================================

        errores = []

        for campo, mensajes in form.errors.items():

            for mensaje in mensajes:

                errores.append(
                    str(mensaje)
                )

        return JsonResponse({
            "success": False,
            "type": "warning",
            "message": " ".join(errores)
        })

    # =========================================================
    # OTROS MÉTODOS
    # =========================================================

    return JsonResponse({
        "success": False,
        "type": "error",
        "message": "Método no permitido."
    }, status=405)


# ============================================================
# EDITAR EVENTO
# ============================================================

def editar_evento(
    request,
    evento_id
):

    evento = get_object_or_404(
        Evento,
        id=evento_id
    )

    # =========================================================
    # MOSTRAR FORMULARIO
    # =========================================================

    if request.method == "GET":

        form = EventoForm(
            instance=evento
        )

        return render(
            request,
            "admin/eventos/form_evento.html",
            {
                "form": form,
                "evento": evento,
                "editar": True,
            }
        )

    # =========================================================
    # PROCESAR FORMULARIO
    # =========================================================

    if request.method == "POST":

        form = EventoForm(
            request.POST,
            request.FILES,
            instance=evento
        )

        if form.is_valid():
            imagen_anterior = evento.imagen if evento.imagen else None
            try:
                evento = form.save(commit=False)
                if form.cleaned_data.get("eliminar_imagen") and not request.FILES.get("imagen"):
                    evento.imagen = None
                evento.save()
                form.save_m2m()
            except Exception:
                return _image_save_error(evento.pk)

            if (
                imagen_anterior
                and imagen_anterior.name
                and imagen_anterior.name != (evento.imagen.name if evento.imagen else "")
            ):
                _schedule_image_delete(imagen_anterior, evento.pk)

            return JsonResponse({
                "success": True,
                "type": "success",
                "message": (
                    f"El evento '{evento.titulo}' "
                    "se actualizó correctamente."
                )
            })

        # =====================================================
        # ERRORES DEL FORMULARIO
        # =====================================================

        errores = []

        for campo, mensajes in form.errors.items():

            for mensaje in mensajes:

                errores.append(
                    str(mensaje)
                )

        return JsonResponse({
            "success": False,
            "type": "warning",
            "message": " ".join(errores)
        })

    # =========================================================
    # MÉTODO NO PERMITIDO
    # =========================================================

    return JsonResponse({
        "success": False,
        "type": "error",
        "message": "Método no permitido."
    }, status=405)


# ============================================================
# ELIMINAR EVENTO
# ============================================================

def eliminar_evento(
    request,
    evento_id
):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "type": "error",
            "message": "Método no permitido.",
        }, status=405)

    evento = get_object_or_404(
        Evento,
        id=evento_id
    )

    titulo = evento.titulo
    imagen = evento.imagen if evento.imagen else None
    evento_id = evento.pk
    evento.delete()
    _schedule_image_delete(imagen, evento_id)

    return JsonResponse({
        "success": True,
        "type": "success",
        "message": f"El evento '{titulo}' se eliminó correctamente.",
        "evento_id": evento_id,
    })


# ============================================================
# DETALLE DEL EVENTO
# ============================================================

def detalle_evento(
    request,
    id
):

    evento = get_object_or_404(
        Evento,
        id=id
    )

    return render(
        request,
        "eventos/detalle_evento.html",
        {
            "evento": evento,
        }
    )


# ============================================================
# LISTAR EVENTOS - ALUMNO
# ============================================================

def listar_eventos_alumno(request):

    eventos = (
        Evento.objects
        .filter(
            publicado=True,
            publico__in=["todos", "alumnos"]
        )
        .order_by(
            "fecha",
            "hora_inicio"
        )
    )

    return render(
        request,
        "admin/eventos/eventos_alumnos.html",
        {
            "eventos": eventos,
        }
    )


# ============================================================
# LISTAR EVENTOS - DOCENTE
# ============================================================

def listar_eventos_docente(request):

    eventos = (
        Evento.objects
        .filter(
            publico__in=["todos", "docentes"],
            publicado=True
        )
        .order_by(
            "fecha",
            "hora_inicio"
        )
    )

    return render(
        request,
        "admin/eventos/eventos_docente.html",
        {
            "eventos": eventos,
        }
    )
