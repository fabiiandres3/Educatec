from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from apps.user.models import Usuario
from apps.alumnos.models import Alumnos
from apps.user.forms import EditarUsuarioForm
from apps.alumnos.forms import AlumnoForm

# Create your views here.


def Listar_alumnos(request):
    alumnos = Usuario.objects.filter(rol__nombre='alumno')

    return render(request, 'admin/alumnos/alumnos.html', {'alumnos':alumnos})


def Editar_alumno(request, alumno_id):

    alumno = get_object_or_404(
        Alumnos,
        usuario_id=alumno_id
    )

    usuario = alumno.usuario

    if request.method == "POST":

        usuario_form = EditarUsuarioForm(
            request.POST,
            instance=usuario
        )

        alumno_form = AlumnoForm(
            request.POST,
            instance=alumno
        )

        if usuario_form.is_valid() and alumno_form.is_valid():

            nuevo_curso = alumno_form.cleaned_data.get("curso")

            # Verificar si se está asignando un curso
            if nuevo_curso:

                cantidad_alumnos = Alumnos.objects.filter(
                    curso=nuevo_curso
                ).exclude(
                    pk=alumno.pk
                ).count()

                if cantidad_alumnos >= 3:

                    messages.error(
                        request,
                        f"El curso {nuevo_curso.nombre} ya alcanzó "
                        "el límite máximo de 32 alumnos."
                    )

                    return render(
                        request,
                        "admin/alumnos/editar_alumno.html",
                        {
                            "usuario_form": usuario_form,
                            "alumno_form": alumno_form,
                        },
                    )

            usuario_form.save()
            alumno_form.save()

            messages.success(
                request,
                "Alumno actualizado correctamente."
            )

            return redirect("listar_alumnos")

    else:

        usuario_form = EditarUsuarioForm(
            instance=usuario
        )

        alumno_form = AlumnoForm(
            instance=alumno
        )

    return render(
        request,
        "admin/alumnos/editar_alumno.html",
        {
            "usuario_form": usuario_form,
            "alumno_form": alumno_form,
        },
    )


def Eliminar_alumno(request, docente_id):
    alumno = get_object_or_404(Alumnos, usuario_id=docente_id)

    if request.method == "POST":
        alumno.usuario.delete()  # Elimina Usuario y Docente si la relación es CASCADE
        return redirect("listar_alumnos")

    return render(
        request,
        "admin/alumnos/eliminar_alumno.html",
        {
            "alumno": alumno,
        },
    )