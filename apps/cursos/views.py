from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
import pandas as pd
from django.db.models import Count
from django.contrib import messages

from apps.user.models import Usuario, Roles
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

    if request.method != 'POST':
        return redirect('listar_cursos')

    if 'archivo_excel' not in request.FILES:
        messages.error(
            request,
            'No se adjuntó ningún archivo Excel.'
        )
        return redirect('listar_cursos')

    archivo = request.FILES['archivo_excel']

    try:

        # =====================================================
        # LEER EXCEL
        # =====================================================

        df = pd.read_excel(archivo)

        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

        print('Columnas detectadas:')
        print(df.columns.tolist())

        print('Filas detectadas:', len(df))

        if df.empty:
            messages.error(
                request,
                'El archivo Excel está vacío.'
            )
            return redirect('listar_cursos')

        # =====================================================
        # COLUMNAS OBLIGATORIAS
        # =====================================================

        columnas_requeridas = {
            'username',
            'first_name',
            'last_name',
            'email',
            'rol',
            'curso',
            'fecha_nacimiento',
            'telefono',
            'direccion',
            'fecha_ingreso',
        }

        faltantes = (
            columnas_requeridas -
            set(df.columns)
        )

        if faltantes:

            faltantes_texto = ', '.join(
                sorted(faltantes)
            )

            messages.error(
                request,
                f'No se pudo importar el archivo porque '
                f'faltan las columnas: {faltantes_texto}.'
            )

            return redirect('listar_cursos')

        df = df.where(
            pd.notnull(df),
            None
        )

        # =====================================================
        # BUSCAR ROL ALUMNO
        # =====================================================

        rol_alumno = Roles.objects.filter(
            nombre__iexact='alumno'
        ).first()

        if not rol_alumno:

            messages.error(
                request,
                'No se pudieron registrar los alumnos porque '
                'el rol "Alumno" no existe en el sistema.'
            )

            return redirect('listar_cursos')

        creados = 0
        actualizados = 0
        errores = []

        # =====================================================
        # PROCESAR CADA FILA
        # =====================================================

        for numero_fila, row in df.iterrows():

            fila_excel = numero_fila + 2

            try:

                # =================================================
                # USERNAME
                # =================================================

                username = row.get('username')

                if username is None:
                    raise ValueError(
                        'el username está vacío'
                    )

                if isinstance(username, float):

                    if username.is_integer():
                        username = str(int(username))
                    else:
                        username = str(username)

                else:
                    username = str(username)

                username = username.strip()

                if not username:
                    raise ValueError(
                        'el username está vacío'
                    )

                # =================================================
                # NOMBRE
                # =================================================

                first_name = row.get('first_name')

                first_name = (
                    str(first_name).strip()
                    if first_name is not None
                    else ''
                )

                # =================================================
                # APELLIDO
                # =================================================

                last_name = row.get('last_name')

                last_name = (
                    str(last_name).strip()
                    if last_name is not None
                    else ''
                )

                nombre_alumno = (
                    f'{first_name} {last_name}'
                ).strip()

                if not nombre_alumno:
                    nombre_alumno = username

                # =================================================
                # EMAIL
                # =================================================

                email = row.get('email')

                if email is None:
                    raise ValueError(
                        'el email está vacío'
                    )

                email = str(email).strip().lower()

                if not email:
                    raise ValueError(
                        'el email está vacío'
                    )

                # =================================================
                # CURSO
                # =================================================

                curso_nombre = row.get('curso')

                if curso_nombre is None:
                    raise ValueError(
                        'el curso está vacío'
                    )

                curso_nombre = str(
                    curso_nombre
                ).strip()

                curso_obj = Cursos.objects.filter(
                    nombre__iexact=curso_nombre
                ).first()

                if not curso_obj:
                    raise ValueError(
                        f'el curso "{curso_nombre}" no existe'
                    )

                # =================================================
                # FECHA NACIMIENTO
                # =================================================

                fecha_nacimiento = row.get(
                    'fecha_nacimiento'
                )

                if fecha_nacimiento is not None:

                    try:

                        fecha_nacimiento = pd.to_datetime(
                            fecha_nacimiento,
                            dayfirst=True,
                            errors='raise'
                        ).date()

                    except Exception:

                        raise ValueError(
                            'la fecha de nacimiento '
                            'no tiene un formato válido'
                        )

                # =================================================
                # TELÉFONO
                # =================================================

                telefono = row.get('telefono')

                if telefono is not None:

                    if isinstance(telefono, float):

                        if telefono.is_integer():

                            telefono = str(
                                int(telefono)
                            )

                        else:

                            telefono = format(
                                telefono,
                                'f'
                            ).rstrip('0').rstrip('.')

                    else:

                        telefono = str(
                            telefono
                        ).strip()

                # =================================================
                # DIRECCIÓN
                # =================================================

                direccion = row.get('direccion')

                direccion = (
                    str(direccion).strip()
                    if direccion is not None
                    else None
                )

                # =================================================
                # FECHA INGRESO
                # =================================================

                fecha_ingreso = row.get(
                    'fecha_ingreso'
                )

                if fecha_ingreso is not None:

                    try:

                        fecha_ingreso = pd.to_datetime(
                            fecha_ingreso,
                            dayfirst=True,
                            errors='raise'
                        ).date()

                    except Exception:

                        raise ValueError(
                            'la fecha de ingreso '
                            'no tiene un formato válido'
                        )

                # =================================================
                # BUSCAR USUARIO
                # =================================================

                usuario_username = Usuario.objects.filter(
                    username=username
                ).first()

                usuario_email = Usuario.objects.filter(
                    email__iexact=email
                ).first()

                # =================================================
                # USUARIO EXISTENTE POR USERNAME
                # =================================================

                if usuario_username:

                    usuario_obj = usuario_username

                    # El email pertenece a otro usuario
                    if (
                        usuario_email and
                        usuario_email.pk != usuario_obj.pk
                    ):

                        raise ValueError(
                            f'el email "{email}" ya está '
                            f'registrado con otro usuario'
                        )

                    usuario_obj.email = email
                    usuario_obj.first_name = first_name
                    usuario_obj.last_name = last_name

                    # Asignar rol Alumno
                    usuario_obj.rol = rol_alumno

                    usuario_obj.save()

                    usuario_creado = False

                # =================================================
                # EMAIL EXISTENTE CON OTRO USERNAME
                # =================================================

                elif usuario_email:

                    raise ValueError(
                        f'el email "{email}" ya está '
                        f'registrado con otro username'
                    )

                # =================================================
                # CREAR USUARIO NUEVO
                # =================================================

                else:

                    usuario_obj = Usuario.objects.create(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        rol=rol_alumno,
                    )

                    # No se utiliza contraseña desde Excel
                    usuario_obj.set_unusable_password()

                    usuario_obj.save()

                    usuario_creado = True

                # =================================================
                # CREAR / ACTUALIZAR ALUMNO
                # =================================================

                with transaction.atomic():

                    Alumnos.objects.update_or_create(
                        usuario=usuario_obj,
                        defaults={
                            'curso': curso_obj,
                            'fecha_nacimiento':
                                fecha_nacimiento,
                            'telefono':
                                telefono,
                            'direccion':
                                direccion,
                            'fecha_ingreso':
                                fecha_ingreso,
                            'activo':
                                True,
                        }
                    )

                # =================================================
                # CONTADORES
                # =================================================

                if usuario_creado:
                    creados += 1
                else:
                    actualizados += 1

            # =====================================================
            # ERROR DE ESTA FILA
            # =====================================================

            except Exception as e:

                mensaje_error = str(e)

                mensaje = (
                    f'El registro "{nombre_alumno}" '
                    f'no se pudo registrar al curso '
                    f'"{curso_nombre}" porque '
                    f'{mensaje_error}.'
                )

                errores.append(mensaje)

                print(
                    f'ERROR FILA {fila_excel}:',
                    repr(e)
                )

                continue

        # =====================================================
        # RESULTADO FINAL
        # =====================================================

        print('\nERRORES DE IMPORTACIÓN:')

        for error in errores:
            print(error)

        # =====================================================
        # TODO CORRECTO
        # =====================================================

        if not errores:

            messages.success(
                request,
                f'Importación completada correctamente. '
                f'{creados} alumnos registrados y '
                f'{actualizados} alumnos actualizados.'
            )

        # =====================================================
        # HUBO ERRORES
        # =====================================================

        else:

            messages.warning(
                request,
                f'Importación finalizada: '
                f'{creados} registrados, '
                f'{actualizados} actualizados y '
                f'{len(errores)} con errores.'
            )

            for error in errores:

                messages.error(
                    request,
                    error
                )

    # =========================================================
    # ERROR GENERAL
    # =========================================================

    except Exception as e:

        print(
            'ERROR GENERAL EN IMPORTACIÓN:',
            repr(e)
        )

        messages.error(
            request,
            f'No se pudo procesar el archivo Excel '
            f'porque ocurrió un error: {str(e)}.'
        )

    return redirect('listar_cursos')

