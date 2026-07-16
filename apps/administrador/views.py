from django.shortcuts import render, redirect, get_object_or_404
from apps.user.models import Usuario
from apps.user.forms import EditarUsuarioForm
from apps.docentes.models import Docente
from apps.administrador.forms import EditarDocenteForm

# Create your views here.


def Listar_docentes(request):
    docentes = Usuario.objects.filter(rol__nombre="docente")

    return render(request, "admin/docente/docentes.html", {"docentes": docentes})


def Editar_docente(request, docente_id):
    docente = get_object_or_404(Docente, usuario_id=docente_id)
    usuario = docente.usuario

    if request.method == "POST":
        usuario_form = EditarUsuarioForm(request.POST, instance=usuario)
        docente_form = EditarDocenteForm(request.POST, instance=docente)

        if usuario_form.is_valid() and docente_form.is_valid():
            usuario_form.save()
            docente_form.save()
            return redirect("listar_docentes")
    else:
        usuario_form = EditarUsuarioForm(instance=usuario)
        docente_form = EditarDocenteForm(instance=docente)

    return render(request,"admin/docente/editar_docente.html",
        {
            "usuario_form": usuario_form,
            "docente_form": docente_form,
        },
    )


def Eliminar_docente(request, docente_id):
    docente = get_object_or_404(Docente, usuario_id=docente_id)

    if request.method == "POST":
        docente.usuario.delete()  # Elimina Usuario y Docente si la relación es CASCADE
        return redirect("listar_docentes")

    return render(
        request,
        "admin/docente/eliminar_docente.html",
        {
            "docente": docente,
        },
    )