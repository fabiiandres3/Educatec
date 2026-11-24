from django.shortcuts import redirect, render, get_object_or_404
from .forms import EventoForm
from .models import Evento
from django.http import JsonResponse
from django.db.models import F, Q
from django.utils import timezone


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

            evento = form.save()

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

            evento = form.save()

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
    evento.delete()

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
    eventos = Evento.objects.all()
    if request.GET.get("origen") == "alumno":
        eventos = eventos.filter(publicado=True, publico__in=["todos", "alumnos"])
    evento = get_object_or_404(eventos, id=id)

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
    ahora = timezone.localtime()
    hoy = timezone.localdate()
    hora_actual = ahora.time()
    visibles = Evento.objects.filter(publicado=True, publico__in=["todos", "alumnos"])

    eventos_proximos = visibles.filter(
        Q(fecha__gt=hoy)
        | Q(fecha=hoy, hora_inicio__isnull=True)
        | Q(fecha=hoy, hora_inicio__gte=hora_actual)
        | Q(fecha=hoy, hora_inicio__lt=hora_actual, hora_fin__gte=hora_actual)
    ).order_by("fecha", F("hora_inicio").asc(nulls_last=True), "pk")
    eventos_pasados = visibles.filter(
        Q(fecha__lt=hoy)
        | Q(fecha=hoy, hora_inicio__lt=hora_actual, hora_fin__isnull=True)
        | Q(fecha=hoy, hora_inicio__lt=hora_actual, hora_fin__lt=hora_actual)
    ).order_by("-fecha", F("hora_inicio").desc(nulls_last=True), "-pk")

    for evento in eventos_proximos:
        evento.dias_restantes = (evento.fecha - hoy).days
        evento.es_hoy = evento.dias_restantes == 0
        evento.en_curso = bool(
            evento.es_hoy
            and evento.hora_inicio
            and evento.hora_inicio <= hora_actual
            and (evento.hora_fin is None or evento.hora_fin > hora_actual)
        )

    return render(
        request,
        "admin/eventos/eventos_alumnos.html",
        {
            "eventos_proximos": eventos_proximos,
            "eventos_pasados": eventos_pasados,
            "tipos_evento": Evento.TIPOS_EVENTO,
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
