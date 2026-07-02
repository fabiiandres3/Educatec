from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .forms import DocenteForm
from apps.user.forms import UsuarioForm
from .models import Docente, Roles
from apps.user.models import Usuario

# Create your views here.


def listar_docentes(request):
    docentes = Docente.objects.all()

    return render(request, "admin/docente/docentes.html", {"docentes": docentes})

def crear_docente(request, docente_id):

    usuario = get_object_or_404(Usuario, id=docente_id)

    if request.method == "POST":
        form = DocenteForm(request.POST)

        if form.is_valid():
            docente = form.save(commit=False)
            docente.usuario = usuario
            docente.save()

            return redirect("listar_docentes")
    else:
        form = DocenteForm()

    return render(
        request,
        "admin/docente/crear_docente.html",
        {
            "form": form,
            "usuario": usuario,
        },
    )


def editar_docente(request, tarea_id):
    docente = get_object_or_404(Docente, id=tarea_id)

    if request.method == "POST":
        form = DocenteForm(request.POST, instance=docente)

        if form.is_valid():
            docente = form.save(commit=False)

            password = form.cleaned_data.get("password")
            if password:
                docente.set_password(password)

            docente.save()
            return redirect("listar_docentes")
    else:
        form = DocenteForm(instance=docente)

    return render(request, "admin/docente/editar_docente.html", {"form": form})


def eliminar_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)

    if request.method == "POST":
        docente.delete()
        return redirect("listar_docentes")

    return render(request, "admin/docente/eliminar_docente.html", {"docente": docente})


def seleccionar_usuario_docente(request):
    usuarios = Usuario.objects.all()

    return render(
        request, "admin/docente/seleccionar_usuario.html", {"usuarios": usuarios}
    )
