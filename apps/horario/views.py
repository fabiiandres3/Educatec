import json

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PeriodoForm, HorarioForm
from .models import Periodo, Horario

from apps.docentes.models import Docente, AsignacionDocente
from apps.cursos.models import Cursos


# ============================================================
# PERIODOS
# ============================================================

def listar_periodos(request):

    periodos = (
        Periodo.objects
        .all()
        .order_by("-anio", "numero")
    )

    return render(
        request,
        "admin/horario/periodo/listar.html",
        {
            "periodos": periodos,
        }
    )


def crear_periodo(request):

    if request.method == "POST":

        form = PeriodoForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Período creado correctamente."
            )

            return redirect("listar_periodos")

    else:

        form = PeriodoForm()

    return render(
        request,
        "admin/horario/periodo/crear.html",
        {
            "form": form,
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
                "Período actualizado correctamente."
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
            "periodo": periodo,
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
            "Período eliminado correctamente."
        )

        return redirect("listar_periodos")

    return render(
        request,
        "admin/horario/periodo/eliminar.html",
        {
            "periodo": periodo,
        }
    )


# ============================================================
# LISTAR HORARIOS
# ============================================================

def listar_horarios(request):

    horarios = (
        Horario.objects
        .select_related(
            "periodo",
            "docente__usuario",
            "curso",
            "clase",
        )
        .order_by(
            "periodo__anio",
            "periodo__numero",
            "curso__nombre",
            "dia",
            "hora_inicio",
        )
    )

    periodos = Periodo.objects.order_by(
        "-anio",
        "-numero"
    )

    cursos = Cursos.objects.order_by(
        "nombre"
    )

    horarios_data = []

    for horario in horarios:

        horarios_data.append({
            "id": horario.id,

            "periodo": horario.periodo_id,
            "periodoNumero": horario.periodo.numero,
            "periodoAnio": horario.periodo.anio,

            "docente": horario.docente_id,
            "docenteNombre": str(horario.docente),

            "curso": horario.curso_id,
            "cursoNombre": horario.curso.nombre,

            "clase": (
                horario.clase_id
                if horario.clase
                else None
            ),

            "claseNombre": (
                str(horario.clase)
                if horario.clase
                else ""
            ),

            "dia": horario.dia,
            "jornada": horario.jornada,

            "horaInicio": horario.hora_inicio.strftime("%H:%M"),
            "horaFin": horario.hora_fin.strftime("%H:%M"),
        })

    return render(
        request,
        "admin/horario/listar_horario.html",
        {
            "horarios": horarios,
            "periodos": periodos,
            "cursos": cursos,
            "horarios_data": horarios_data,
        }
    )


# ============================================================
# CREAR HORARIO NORMAL
# ============================================================

def crear_horario(request):

    periodos = Periodo.objects.all()

    cursos = Cursos.objects.all()

    # Cursos que ya tienen un horario creado.
    #
    # Se mantiene para que puedas utilizarlo en el template
    # si quieres deshabilitar visualmente esos cursos.
    cursos_con_horario = set(
        Horario.objects.values_list(
            "curso_id",
            flat=True
        )
    )

    return render(
        request,
        "admin/horario/crear_horario.html",
        {
            "periodos": periodos,
            "cursos": cursos,
            "cursos_con_horario": cursos_con_horario,
        }
    )


# ============================================================
# EDITAR HORARIO NORMAL
# ============================================================

def editar_horario(request, periodo_id, curso_id):

    periodo = get_object_or_404(
        Periodo,
        id=periodo_id
    )

    curso = get_object_or_404(
        Cursos,
        id=curso_id
    )

    # =====================================================
    # HORARIOS DEL PERÍODO + CURSO
    # =====================================================

    horarios_queryset = (
        Horario.objects
        .filter(
            periodo_id=periodo_id,
            curso_id=curso_id
        )
        .select_related(
            "periodo",
            "docente",
            "curso",
            "clase"
        )
        .order_by(
            "hora_inicio"
        )
    )

    # =====================================================
    # GUARDAR CAMBIOS
    # =====================================================

    if request.method == "POST":

        try:

            with transaction.atomic():

                # =================================================
                # EDITAR HORARIOS EXISTENTES
                # =================================================

                for horario in horarios_queryset:

                    prefijo = f"horario_{horario.id}"

                    dia = request.POST.get(
                        f"{prefijo}_dia"
                    )

                    jornada = request.POST.get(
                        f"{prefijo}_jornada"
                    )

                    hora_inicio = request.POST.get(
                        f"{prefijo}_hora_inicio"
                    )

                    hora_fin = request.POST.get(
                        f"{prefijo}_hora_fin"
                    )

                    docente_id = request.POST.get(
                        f"{prefijo}_docente"
                    )

                    clase_id = request.POST.get(
                        f"{prefijo}_clase"
                    )

                    if not (
                        dia
                        and jornada
                        and hora_inicio
                        and hora_fin
                    ):
                        continue

                    horario.dia = dia
                    horario.jornada = jornada
                    horario.hora_inicio = hora_inicio
                    horario.hora_fin = hora_fin

                    if docente_id:
                        horario.docente_id = docente_id

                    if clase_id:
                        horario.clase_id = clase_id

                    horario.save()

                # =================================================
                # CREAR NUEVOS HORARIOS
                # =================================================

                nuevos = request.POST.get(
                    "nuevos_horarios"
                )

                if nuevos:

                    nuevos_ids = nuevos.split(",")

                    for nuevo_id in nuevos_ids:

                        nuevo_id = nuevo_id.strip()

                        if not nuevo_id:
                            continue

                        dia = request.POST.get(
                            f"nuevo_{nuevo_id}_dia"
                        )

                        jornada = request.POST.get(
                            f"nuevo_{nuevo_id}_jornada"
                        )

                        hora_inicio = request.POST.get(
                            f"nuevo_{nuevo_id}_hora_inicio"
                        )

                        hora_fin = request.POST.get(
                            f"nuevo_{nuevo_id}_hora_fin"
                        )

                        docente_id = request.POST.get(
                            f"nuevo_{nuevo_id}_docente"
                        )

                        clase_id = request.POST.get(
                            f"nuevo_{nuevo_id}_clase"
                        )

                        if not docente_id:
                            continue

                        if not clase_id:
                            continue

                        if not dia:
                            continue

                        if not jornada:
                            continue

                        if not hora_inicio:
                            continue

                        if not hora_fin:
                            continue

                        # -----------------------------------------
                        # VALIDAR CONFLICTO DEL CURSO
                        # -----------------------------------------

                        conflicto_curso = Horario.objects.filter(
                            periodo_id=periodo_id,
                            curso_id=curso_id,
                            dia=dia,
                            hora_inicio__lt=hora_fin,
                            hora_fin__gt=hora_inicio,
                        ).exists()

                        if conflicto_curso:

                            raise ValueError(
                                "El curso ya tiene otra clase "
                                "programada en ese horario."
                            )

                        # -----------------------------------------
                        # VALIDAR CONFLICTO DEL DOCENTE
                        # -----------------------------------------

                        conflicto_docente = Horario.objects.filter(
                            periodo_id=periodo_id,
                            docente_id=docente_id,
                            dia=dia,
                            hora_inicio__lt=hora_fin,
                            hora_fin__gt=hora_inicio,
                        ).exists()

                        if conflicto_docente:

                            raise ValueError(
                                "El docente ya tiene otra "
                                "asignación en ese horario."
                            )

                        Horario.objects.create(
                            periodo_id=periodo_id,
                            docente_id=docente_id,
                            curso_id=curso_id,
                            clase_id=clase_id,
                            dia=dia,
                            jornada=jornada,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin,
                        )

            messages.success(
                request,
                "Horario actualizado correctamente."
            )

            return redirect(
                "listar_horarios"
            )

        except Exception as e:

            messages.error(
                request,
                f"Error al actualizar el horario: {e}"
            )

    # =====================================================
    # DATOS PARA JAVASCRIPT
    # =====================================================

    horarios_data = []

    for horario in horarios_queryset:

        horarios_data.append({

            "id": horario.id,

            "periodo": horario.periodo_id,

            "docente": horario.docente_id,

            "docenteId": horario.docente_id,

            "docenteNombre": str(
                horario.docente
            ),

            "curso": horario.curso_id,

            "cursoNombre": horario.curso.nombre,

            "clase": (
                horario.clase_id
                if horario.clase_id
                else None
            ),

            "claseNombre": (
                str(horario.clase)
                if horario.clase_id
                else ""
            ),

            "dia": horario.dia,

            "jornada": horario.jornada,

            "horaInicio": (
                horario.hora_inicio.strftime("%H:%M")
            ),

            "horaFin": (
                horario.hora_fin.strftime("%H:%M")
            ),

        })

    # =====================================================
    # DOCENTES
    # =====================================================

    docentes = (
        Docente.objects
        .select_related("usuario")
        .order_by(
            "usuario__first_name",
            "usuario__last_name"
        )
    )

    # =====================================================
    # CLASES DEL CURSO
    # =====================================================

    clases = curso.clases.all()

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "admin/horario/editar_horario.html",
        {
            "periodo": periodo,
            "curso": curso,
            "horarios_data": horarios_data,
            "docentes": docentes,
            "clases": clases,
        }
    )


# ============================================================
# ELIMINAR HORARIO NORMAL
# ============================================================

def eliminar_horario(request, id):

    horario = get_object_or_404(
        Horario,
        pk=id
    )

    if request.method == "POST":

        horario.delete()

        messages.success(
            request,
            "Horario eliminado correctamente."
        )

        return redirect(
            "listar_horarios"
        )

    return render(
        request,
        "horarios/eliminar_horario.html",
        {
            "horario": horario,
        }
    )


# ============================================================
# PLANIFICADOR VISUAL
# ============================================================

def listar_horario(request):

    periodos = Periodo.objects.all().order_by("id")

    cursos = Cursos.objects.all().order_by("id")

    asignaciones = (
        AsignacionDocente.objects
        .select_related(
            "docente__usuario",
            "clase__curso"
        )
    )

    horarios = (
        Horario.objects
        .select_related(
            "periodo",
            "docente__usuario",
            "curso",
            "clase"
        )
    )

    return render(
        request,
        "admin/horario/listar_horario.html",
        {
            "periodos": periodos,
            "cursos": cursos,
            "asignaciones": asignaciones,
            "horarios": horarios,
        }
    )


# ============================================================
# CREAR HORARIO POR CURSO
# ============================================================

def crear_horario_curso(request, periodo_id, curso_id):

    periodo = get_object_or_404(
        Periodo,
        id=periodo_id
    )

    curso = get_object_or_404(
        Cursos,
        id=curso_id
    )

    # =====================================================
    # VALIDAR SI YA EXISTE HORARIO
    # =====================================================

    horario_existente = Horario.objects.filter(
        periodo_id=periodo_id,
        curso_id=curso_id
    ).exists()

    if horario_existente:

        messages.warning(
            request,
            "Este curso ya tiene un horario creado para este período."
        )

        return redirect(
            "listar_horario"
        )

    # =====================================================
    # OBTENER DOCENTES ASIGNADOS AL CURSO
    # =====================================================

    asignaciones = (
        AsignacionDocente.objects
        .filter(
            curso=curso
        )
        .select_related(
            "docente__usuario",
            "curso",
        )
    )

    dias = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miércoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
    ]

    horas_manana = [
        ("06:00", "07:00"),
        ("07:00", "08:00"),
        ("08:00", "09:00"),
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "12:00"),
    ]

    horas_tarde = [
        ("12:30", "13:30"),
        ("13:30", "14:30"),
        ("14:30", "15:30"),
        ("15:30", "16:30"),
        ("16:30", "17:00"),
    ]

    return render(
        request,
        "admin/horario/crear_horario_curso.html.html",
        {
            "periodo": periodo,
            "curso": curso,
            "asignaciones": asignaciones,
            "dias": dias,
            "horas_manana": horas_manana,
            "horas_tarde": horas_tarde,
        },
    )


    periodo = get_object_or_404(
        Periodo,
        id=periodo_id
    )

    curso = get_object_or_404(
        Cursos,
        id=curso_id
    )

    # =====================================================
    # VALIDAR SI YA EXISTE HORARIO
    # =====================================================

    horario_existente = Horario.objects.filter(
        periodo_id=periodo_id,
        curso_id=curso_id
    ).exists()

    if horario_existente:

        messages.warning(
            request,
            "Este curso ya tiene un horario creado para este período."
        )

        return redirect(
            "listar_horario"
        )

    asignaciones = (
        AsignacionDocente.objects
        .filter(
            clase__curso=curso
        )
        .select_related(
            "docente__usuario",
            "clase",
            "clase__curso",
        )
    )

    dias = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miércoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
    ]

    horas_manana = [
        ("06:00", "07:00"),
        ("07:00", "08:00"),
        ("08:00", "09:00"),
        ("09:00", "10:00"),
        ("10:00", "11:00"),
        ("11:00", "12:00"),
    ]

    horas_tarde = [
        ("12:30", "13:30"),
        ("13:30", "14:30"),
        ("14:30", "15:30"),
        ("15:30", "16:30"),
        ("16:30", "17:00"),
    ]

    return render(
        request,
        "admin/horario/crear_horario_curso.html.html",
        {
            "periodo": periodo,
            "curso": curso,
            "asignaciones": asignaciones,
            "dias": dias,
            "horas_manana": horas_manana,
            "horas_tarde": horas_tarde,
        },
    )


# ============================================================
# VALIDAR CONFLICTOS
# ============================================================

def validar_conflictos_horario(horario):

    # --------------------------------------------------------
    # CONFLICTO DEL CURSO
    # --------------------------------------------------------

    conflictos_curso = Horario.objects.filter(
        periodo=horario.periodo,
        curso=horario.curso,
        dia=horario.dia,
        hora_inicio__lt=horario.hora_fin,
        hora_fin__gt=horario.hora_inicio,
    )

    if horario.pk:

        conflictos_curso = conflictos_curso.exclude(
            pk=horario.pk
        )

    conflicto_curso = conflictos_curso.first()

    if conflicto_curso:

        raise ValueError(
            f"El curso {horario.curso} ya tiene "
            f"otra clase programada el "
            f"{horario.get_dia_display()} de "
            f"{horario.hora_inicio.strftime('%H:%M')} "
            f"a "
            f"{horario.hora_fin.strftime('%H:%M')}."
        )

    # --------------------------------------------------------
    # CONFLICTO DEL DOCENTE
    # --------------------------------------------------------

    conflictos_docente = Horario.objects.filter(
        periodo=horario.periodo,
        docente=horario.docente,
        dia=horario.dia,
        hora_inicio__lt=horario.hora_fin,
        hora_fin__gt=horario.hora_inicio,
    )

    if horario.pk:

        conflictos_docente = conflictos_docente.exclude(
            pk=horario.pk
        )

    conflicto_docente = conflictos_docente.first()

    if conflicto_docente:

        raise ValueError(
            f"El docente {horario.docente} ya tiene "
            f"otra asignación el "
            f"{horario.get_dia_display()} de "
            f"{horario.hora_inicio.strftime('%H:%M')} "
            f"a "
            f"{horario.hora_fin.strftime('%H:%M')}."
        )


# ============================================================
# GUARDAR HORARIO DESDE EL PLANIFICADOR
# ============================================================

@require_POST
def guardar_horario_ajax(request):

    try:

        # ====================================================
        # RECIBIR DATOS
        # ====================================================

        datos = request.POST.get("horarios")

        if not datos:

            return JsonResponse(
                {
                    "ok": False,
                    "mensaje": "No se recibieron horarios para guardar."
                },
                status=400
            )

        try:

            horarios_recibidos = json.loads(datos)

        except (json.JSONDecodeError, TypeError):

            return JsonResponse(
                {
                    "ok": False,
                    "mensaje": "Los datos enviados no tienen un formato válido."
                },
                status=400
            )

        if not isinstance(horarios_recibidos, list):

            return JsonResponse(
                {
                    "ok": False,
                    "mensaje": "El formato de los horarios no es válido."
                },
                status=400
            )

        if not horarios_recibidos:

            return JsonResponse(
                {
                    "ok": False,
                    "mensaje": "No hay horarios seleccionados para guardar."
                },
                status=400
            )

        # ====================================================
        # CONTADORES
        # ====================================================

        creados = 0
        actualizados = 0

        # ====================================================
        # TRANSACCIÓN
        # ====================================================

        with transaction.atomic():

            for item in horarios_recibidos:

                if not isinstance(item, dict):

                    raise ValueError(
                        "Uno de los horarios enviados no es válido."
                    )

                horario_id = item.get("id")

                periodo_id = item.get("periodo")
                docente_id = item.get("docente")
                curso_id = item.get("curso")
                clase_id = item.get("clase")
                dia = item.get("dia")
                jornada = item.get("jornada")

                hora_inicio = (
                    item.get("horaInicio")
                    or item.get("hora_inicio")
                )

                hora_fin = (
                    item.get("horaFin")
                    or item.get("hora_fin")
                )

                # ====================================================
                # VALIDACIONES BÁSICAS
                # ====================================================

                if not periodo_id:

                    raise ValueError(
                        "Falta seleccionar el período."
                    )

                if not docente_id:

                    raise ValueError(
                        "Falta seleccionar el docente."
                    )

                if not curso_id:

                    raise ValueError(
                        "Falta seleccionar el curso."
                    )

                if not clase_id:

                    raise ValueError(
                        "Falta seleccionar la materia o clase."
                    )

                if not dia:

                    raise ValueError(
                        "Falta indicar el día del horario."
                    )

                if not jornada:

                    raise ValueError(
                        "Falta indicar la jornada."
                    )

                if not hora_inicio or not hora_fin:

                    raise ValueError(
                        "Falta indicar el rango de horas."
                    )

                # ====================================================
                # DATOS PARA EL FORMULARIO
                # ====================================================

                datos_form = {
                    "periodo": periodo_id,
                    "docente": docente_id,
                    "curso": curso_id,
                    "clase": clase_id,
                    "dia": dia,
                    "jornada": jornada,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                }

                # ====================================================
                # CREAR / EDITAR
                # ====================================================

                if horario_id:

                    # =================================================
                    # EDITAR
                    # =================================================

                    horario = get_object_or_404(
                        Horario,
                        pk=horario_id
                    )

                    form = HorarioForm(
                        data=datos_form,
                        instance=horario
                    )

                    es_nuevo = False

                else:

                    # =================================================
                    # CREAR
                    # =================================================

                    # IMPORTANTE:
                    #
                    # Un curso solamente puede tener UN registro
                    # de horario dentro del mismo período.
                    #
                    # Ejemplo:
                    #
                    # Período 1 + Curso 5B -> ya existe
                    #
                    # No se permite:
                    #
                    # Período 1 + Curso 5B -> segundo registro
                    #
                    # Aunque cambien docente, clase, día u hora.

                    horario_existente = Horario.objects.filter(
                        periodo_id=periodo_id,
                        curso_id=curso_id
                    ).exists()

                    if horario_existente:

                        raise ValueError(
                            "El curso seleccionado ya tiene un "
                            "horario registrado para este período."
                        )

                    horario = Horario()

                    form = HorarioForm(
                        data=datos_form
                    )

                    es_nuevo = True

                # ====================================================
                # VALIDAR FORMULARIO
                # ====================================================

                if not form.is_valid():

                    nombres_campos = {
                        "periodo": "Período",
                        "docente": "Docente",
                        "curso": "Curso",
                        "clase": "Materia",
                        "dia": "Día",
                        "jornada": "Jornada",
                        "hora_inicio": "Hora de inicio",
                        "hora_fin": "Hora de finalización",
                    }

                    errores = []

                    for campo, mensajes_error in form.errors.items():

                        for mensaje in mensajes_error:

                            if campo == "__all__":

                                errores.append(
                                    str(mensaje)
                                )

                            else:

                                nombre = nombres_campos.get(
                                    campo,
                                    campo
                                )

                                errores.append(
                                    f"{nombre}: {mensaje}"
                                )

                    raise ValueError(
                        " | ".join(errores)
                    )

                # ====================================================
                # CREAR INSTANCIA SIN GUARDAR
                # ====================================================

                instancia = form.save(
                    commit=False
                )

                # ====================================================
                # VALIDAR HORAS
                # ====================================================

                if instancia.hora_inicio >= instancia.hora_fin:

                    raise ValueError(
                        "La hora de inicio debe ser menor "
                        "que la hora de finalización."
                    )

                # ====================================================
                # VALIDAR CONFLICTOS
                # ====================================================

                validar_conflictos_horario(
                    instancia
                )

                # ====================================================
                # GUARDAR
                # ====================================================

                instancia.save()

                if es_nuevo:

                    creados += 1

                else:

                    actualizados += 1

        # ====================================================
        # MENSAJE FINAL
        # ====================================================

        if creados and actualizados:

            mensaje = (
                f"Horario guardado correctamente. "
                f"{creados} horario(s) creado(s) y "
                f"{actualizados} actualizado(s)."
            )

        elif creados:

            mensaje = (
                f"{creados} horario(s) creado(s) correctamente."
            )

        elif actualizados:

            mensaje = (
                f"{actualizados} horario(s) actualizado(s) correctamente."
            )

        else:

            mensaje = (
                "No se realizaron cambios."
            )

        return JsonResponse(
            {
                "ok": True,
                "mensaje": mensaje,
            }
        )

    except ValueError as error:

        return JsonResponse(
            {
                "ok": False,
                "mensaje": str(error),
            },
            status=400
        )

    except Horario.DoesNotExist:

        return JsonResponse(
            {
                "ok": False,
                "mensaje": (
                    "Uno de los horarios que intentas editar "
                    "ya no existe en la base de datos."
                ),
            },
            status=400
        )

    except Exception as error:

        print("=" * 60)
        print("ERROR GUARDAR HORARIO")
        print(repr(error))
        print("=" * 60)

        return JsonResponse(
            {
                "ok": False,
                "mensaje": (
                    "Ocurrió un error al guardar el horario. "
                    "Revisa la consola de Django."
                ),
            },
            status=500
        )