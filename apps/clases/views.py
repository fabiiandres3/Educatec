from django.shortcuts import render, redirect
from apps.clases.forms import ClaseForm
from .models import Clases

# Create your views here.


def Listar_Clases(request):
    clases = Clases.objects.prefetch_related("cursos").all()
    clases_con_curso = clases.filter(cursos__isnull=False).distinct().count()
    clases_sin_curso = clases.filter(cursos__isnull=True).count()
    return render(request, "admin/clases/clases.html", {
        "clases": clases,
        "clases_con_curso": clases_con_curso,
        "clases_sin_curso": clases_sin_curso,
    })

def Crear_clase(request):
    if request.method == 'POST':
        form = ClaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clases')
    else:
        form = ClaseForm()
    return render(request, 'admin/clases/crear_clases.html', {'form': form})

def Editar_clase(request, clase_id):
    clase = Clases.objects.get(id=clase_id)
    if request.method == 'POST':
        form = ClaseForm(request.POST, instance=clase)
        if form.is_valid():
            form.save()
            return redirect('clases')
    else:
        form = ClaseForm(instance=clase)
    return render(request, 'admin/clases/editar_clases.html', {'form': form, 'clase': clase})

def Eliminar_clase(request, clase_id):
    clase = Clases.objects.get(id=clase_id)
    clase.delete()
    return redirect('clases')