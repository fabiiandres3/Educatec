from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PeriodoForm, HorarioForm
from .models import Periodo, Horario


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
        "admin/horario/periodo/formulario.html",
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
        "admin/horario/periodo/formulario.html",
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


def listar_horarios(request):

    horarios = Horario.objects.select_related(
        "docente",
        "periodo"
    ).all()

    return render(
        request,
        "horarios/listar_horarios.html",
        {
            "horarios": horarios
        }
    )


def crear_horario(request):

    if request.method == "POST":

        form = HorarioForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El horario fue creado correctamente."
            )

            return redirect("listar_horarios")

    else:

        form = HorarioForm()

    return render(
        request,
        "horarios/crear_horario.html",
        {
            "form": form
        }
    )


def editar_horario(request, id):

    horario = get_object_or_404(
        Horario,
        id=id
    )

    if request.method == "POST":

        form = HorarioForm(
            request.POST,
            instance=horario
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El horario fue actualizado correctamente."
            )

            return redirect("listar_horarios")

    else:

        form = HorarioForm(
            instance=horario
        )

    return render(
        request,
        "horarios/editar_horario.html",
        {
            "form": form,
            "horario": horario
        }
    )


def eliminar_horario(request, id):

    horario = get_object_or_404(
        Horario,
        id=id
    )

    if request.method == "POST":

        horario.delete()

        messages.success(
            request,
            "El horario fue eliminado correctamente."
        )

    return redirect("listar_horarios")