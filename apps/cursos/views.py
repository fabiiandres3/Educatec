from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib import messages

from apps.user.models import Usuario
from apps.alumnos.models import Alumnos

from .forms import CursosForm
from .models import Cursos


# ==========================================
# LISTAR CURSOS + ALUMNOS
# URL: /listar_cursos/
# ==========================================

def listar_cursos(request):

    cursos = Cursos.objects.annotate(
    cantidad_alumnos=Count("alumnos"))

    alumnos = Alumnos.objects.select_related(
        "usuario",
        "curso",
        "clase"
    ).all()

    return render(
        request,
        "admin/cursos/cursos.html",
        {
            "cursos": cursos,
            "alumnos": alumnos,
        }
    )


# ==========================================
# LISTAR SOLO ALUMNOS
# URL: /listar_alumnos/
# ==========================================

def listar_alumnos(request):

    alumnos = Alumnos.objects.select_related(
        "usuario",
        "curso",
        "clase"
    ).all()

    return render(
        request,
        "admin/cursos/cursos.html",
        {
            "alumnos": alumnos,
        }
    )


# ==========================================
# CREAR CURSO
# ==========================================

def Crear_curso(request):

    if request.method == "POST":

        form = CursosForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            messages.success(request, "Curso creado correctamente.")

            return redirect("listar_cursos")

    else:

        form = CursosForm()

    return render(
        request,"admin/cursos/crear_curso.html",
        {
            "form": form
        }
    )


# ==========================================
# EDITAR CURSO
# ==========================================

def Editar_curso(request, curso_id):

    curso = get_object_or_404(Cursos, id=curso_id)

    if request.method == "POST":

        form = CursosForm(
            request.POST,
            request.FILES,
            instance=curso
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Curso actualizado correctamente."
            )

            return redirect("listar_cursos")

    else:

        form = CursosForm(
            instance=curso
        )

    return render(
        request,
        "admin/cursos/editar_curso.html",
        {
            "form": form,
            "curso": curso
        }
    )


# ==========================================
# ELIMINAR CURSO
# ==========================================

def Eliminar_curso(request, curso_id):

    curso = get_object_or_404(
        Cursos,
        id=curso_id
    )

    curso.delete()

    messages.success(
        request,
        "Curso eliminado correctamente."
    )

    return redirect("listar_cursos")


# ==========================================
# ASIGNAR ALUMNO A CURSO
# ==========================================


def filtrar_alumnos(request):

    curso_id = request.GET.get("curso_id")

    print("CURSO RECIBIDO:", curso_id)

    alumnos = Alumnos.objects.select_related(
        "usuario",
        "curso",
        "clase"
    ).all()

    if curso_id:
        alumnos = alumnos.filter(
            curso_id=curso_id
        )

    return render(
        request,
        "admin/cursos/partials/tabla_alumnos.html",
        {
            "alumnos": alumnos
        }
    )


def asignar_alumno_curso(
    request,
    alumno_id,
    curso_id
):

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    curso = get_object_or_404(
        Cursos,
        id=curso_id
    )

    # --------------------------------------
    # Verificar si ya tiene curso
    # --------------------------------------

    if alumno.curso is not None:

        messages.error(
            request,
            "Este alumno ya está asignado a un curso."
        )

        return redirect("listar_cursos")


    # --------------------------------------
    # Contar alumnos del curso
    # --------------------------------------

    cantidad_alumnos = Usuario.objects.filter(
        curso=curso,
        rol__nombre="alumno"
    ).count()


    # --------------------------------------
    # Verificar límite de 32 alumnos
    # --------------------------------------

    if cantidad_alumnos >= 32:

        messages.error(
            request,
            "No se puede asignar el alumno. "
            "El curso ya tiene 32 alumnos."
        )

        return redirect("listar_cursos")


    # --------------------------------------
    # Asignar curso al alumno
    # --------------------------------------

    alumno.curso = curso

    alumno.save()


    messages.success(
        request,
        "Alumno asignado correctamente."
    )

    return redirect("listar_cursos")