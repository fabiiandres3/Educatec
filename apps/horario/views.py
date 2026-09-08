from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PeriodoForm
from .models import Periodo


def listar_periodos(request):
    periodos = Periodo.objects.all()

    return render(
        request,
        "admin/horario/periodo/listar.html",
        {
            "periodos": periodos
        }
    )


def crear_periodo(request):

    if request.method == "POST":

        form = PeriodoForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El período fue creado correctamente."
            )

            return redirect("listar_periodos")

    else:

        form = PeriodoForm()

    return render(
        request,
        "horario/periodos/formulario.html",
        {
            "form": form,
            "titulo": "Crear período"
        }
    )


def editar_periodo(request, pk):

    periodo = get_object_or_404(
        Periodo,
        pk=pk
    )

    if request.method == "POST":

        form = PeriodoForm(
            request.POST,
            instance=periodo
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El período fue actualizado correctamente."
            )

            return redirect("listar_periodos")

    else:

        form = PeriodoForm(
            instance=periodo
        )

    return render(
        request,
        "horario/periodos/formulario.html",
        {
            "form": form,
            "titulo": "Editar período"
        }
    )


def eliminar_periodo(request, pk):

    periodo = get_object_or_404(
        Periodo,
        pk=pk
    )

    if request.method == "POST":

        periodo.delete()

        messages.success(
            request,
            "El período fue eliminado correctamente."
        )

    return redirect("listar_periodos")