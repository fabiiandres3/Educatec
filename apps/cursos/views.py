from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.user.models import Usuario
from .forms import CursosForm
from .models import Cursos
from apps.alumnos.models import Alumnos
from .filter import obtener_alumnos

# Create your views here.


def Listar_cursos(request):
    cursos = Cursos.objects.all()
    return render(request, 'admin/cursos/cursos.html', {'cursos': cursos})

def Crear_curso(request):
    if request.method == 'POST':
        form = CursosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_cursos')
    else:
        form = CursosForm()
    return render(request, 'admin/cursos/crear_curso.html', {'form': form})

def Editar_curso(request, curso_id):
    curso = get_object_or_404(Cursos, id=curso_id)

    if request.method == 'POST':
        form = CursosForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect('listar_cursos')
    else:
        form = CursosForm(instance=curso)

    return render(request, 'admin/cursos/editar_curso.html', {'form': form, 'curso':curso})

def Eliminar_curso(request, curso_id):
    curso = get_object_or_404(Cursos, id=curso_id)
    curso.delete()
    return redirect('listar_cursos')


def listar_alumnos(request):

    #alumnos = obtener_alumnos()
    alumnos = Alumnos.objecta.all()

    return render(
        request,
        "admin/cursos/cursos.html",
        {
            "alumnos": alumnos
        }
    )


def asignar_alumno_curso(request, alumno_id, curso_id):

    alumno = get_object_or_404(Usuario, id=alumno_id)
    curso = get_object_or_404(Cursos, id=curso_id)

    # Verificar si ya tiene curso
    if alumno.curso is not None:
        messages.error(
            request,
            'Este alumno ya está asignado a un curso.'
        )
        return redirect('listar_alumnos')

    # Contar alumnos del curso
    cantidad_alumnos = Usuario.objects.filter(
        curso=curso,
        rol__nombre='alumno'
    ).count()

    # Límite máximo
    if cantidad_alumnos >= 32:
        messages.error(
            request,
            'No se puede asignar el alumno. El curso ya tiene 32 alumnos.'
        )
        return redirect('listar_alumnos')

    # Asignar
    alumno.curso = curso
    alumno.save()

    messages.success(
        request,
        'Alumno asignado correctamente.'
    )

    return redirect('listar_alumnos')