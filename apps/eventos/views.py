from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .forms import EventoForm
from .models import Evento
from django.http import JsonResponse




def listar_eventos(request):

    eventos = Evento.objects.all().order_by(
        "fecha",
        "hora_inicio"
    )

    return render(
        request,
        "admin/eventos/listar_eventos.html",
        {
            "eventos": eventos,
        }
    )


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

                errores.append(str(mensaje))


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



from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render


def editar_evento(request, evento_id):

    evento = get_object_or_404(
        Evento,
        id=evento_id
    )

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

        errores = []

        for campo, mensajes in form.errors.items():
            for mensaje in mensajes:
                errores.append(str(mensaje))

        return JsonResponse({
            "success": False,
            "type": "warning",
            "message": " ".join(errores)
        })

    return JsonResponse({
        "success": False,
        "type": "error",
        "message": "Método no permitido."
    }, status=405)


def eliminar_evento(request, evento_id):

    evento = get_object_or_404(
        Evento,
        id=evento_id
    )

    if request.method == "POST":

        evento.delete()

        return redirect(
            "listar_eventos"
        )

    return render(
        request,
        "admin/eventos/eliminar_evento.html",
        {
            "evento": evento,
        }
    )

def detalle_evento(request, id):

    evento = get_object_or_404(
        Evento,
        id=id,
        activo=True
    )

    return render(
        request,
        "eventos/detalle_evento.html",
        {
            "evento": evento,
        }
    )


def listar_eventos_alumno(request): 
    eventos = Evento.objects.filter( publicado=True ).order_by( "fecha", "hora" ) 
    return render( request, "admin/eventos/eventos_alumnos.html", { "eventos": eventos, } ) 

def listar_eventos_docente(request): 
    eventos = Evento.objects.filter( publicado=True ).order_by( "fecha", "hora" ) 
    return render( request, "admin/eventos/eventos_docente.html", { "eventos": eventos, } )