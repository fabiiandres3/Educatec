from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EventoForm
from .models import Evento


@login_required
def listar_eventos(request):

    eventos = Evento.objects.all().order_by("fecha", "hora")

    return render(
        request,
        "admin/eventos/listar_eventos.html",
        {
            "eventos": eventos,
        }
    )


@login_required
def crear_evento(request):

    if request.method == "POST":

        form = EventoForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            return redirect("listar_eventos")

    else:

        form = EventoForm()

    return render(
        request,
        "admin/eventos/form_evento.html",
        {
            "form": form,
        }
    )