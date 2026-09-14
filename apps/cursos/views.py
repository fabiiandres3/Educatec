from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
import pandas as pd
from django.db.models import Count
from django.contrib import messages

from apps.user.models import Usuario
from apps.alumnos.models import Alumnos

from .forms import CursosForm
from .models import Cursos


from apps.clases.models import Clases

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



def cargar_alumnos_excel(request):
    if request.method == 'POST':
        if 'archivo_excel' not in request.FILES:
            messages.error(request, "No se adjuntó ningún archivo Excel.")
            return redirect('cursos')

        file = request.FILES['archivo_excel']

        try:
            df = pd.read_excel(file)
            print("Filas detectadas en el Excel:", len(df))  # Imprime en consola de terminal

            # Reemplazar valores nulos
            df = df.where(pd.notnull(df), None)

            creados = 0
            omitidos = 0

            with transaction.atomic():
                for index, row in df.iterrows():
                    # Convertir username
                    val_username = row.get('username')
                    if val_username is None:
                        continue
                    
                    username = str(int(val_username) if isinstance(val_username, float) else val_username).strip()
                    email = str(row.get('email')).strip() if row.get('email') else None

                    if not username or not email:
                        continue

                    if Usuario.objects.filter(username=username).exists():
                        omitidos += 1
                        continue

                    usuario = Usuario.objects.create_user(
                        username=username,
                        email=email,
                        password=str(row.get('password', 'Alumno2026*')),
                        first_name=str(row.get('first_name', '') or ''),
                        last_name=str(row.get('last_name', '') or '')
                    )

                    curso_id = row.get('curso_id')
                    clase_id = row.get('clase_id')

                    curso_obj = Cursos.objects.filter(id=int(curso_id)).first() if curso_id and pd.notnull(curso_id) else None
                    clase_obj = Clases.objects.filter(id=int(clase_id)).first() if clase_id and pd.notnull(clase_id) else None

                    Alumnos.objects.create(
                        usuario=usuario,
                        codigo=str(row.get('codigo')).strip() if row.get('codigo') and pd.notnull(row.get('codigo')) else None,
                        curso=curso_obj,
                        clase=clase_obj,
                        fecha_nacimiento=row.get('fecha_nacimiento') if pd.notnull(row.get('fecha_nacimiento')) else None,
                        telefono=str(row.get('telefono')).strip() if row.get('telefono') and pd.notnull(row.get('telefono')) else None,
                        direccion=str(row.get('direccion')).strip() if row.get('direccion') and pd.notnull(row.get('direccion')) else None,
                        fecha_ingreso=row.get('fecha_ingreso') if pd.notnull(row.get('fecha_ingreso')) else None
                    )
                    creados += 1

            messages.success(request, f"Éxito: {creados} alumnos creados. ({omitidos} omitidos por usuario existente)")

        except Exception as e:
            print("ERROR EN VISTA:", str(e))  # Muestra el error en la terminal
            messages.error(request, f"Error al procesar el Excel: {str(e)}")

    return redirect('listar_cursos')  # Asegúrate de colocar el name de tu URL