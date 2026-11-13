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
        "admin/horario/periodo/formulario.html",
        {
            "form": form,
            "titulo": "Crear período",
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
            "titulo": "Editar período",
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

    cursos = Cursos.objects.all().order_by("nombre")

    asignaciones_docente_curso = list(
        AsignacionDocente.objects
        .filter(curso__isnull=False, clase__isnull=False)
        .values_list("docente_id", "curso_id")
        .distinct()
    )
    docentes_ids = sorted({docente_id for docente_id, _ in asignaciones_docente_curso})
    docentes = (
        Docente.objects.filter(id__in=docentes_ids)
        .select_related("usuario")
        .order_by("usuario__first_name", "usuario__last_name")
    )
    cursos_por_docente = {}
    for docente_id, curso_id in asignaciones_docente_curso:
        cursos_por_docente.setdefault(str(docente_id), []).append(curso_id)

    parejas_periodo_curso_con_horario = list(
        Horario.objects
        .values_list(
            "periodo_id",
            "curso_id",
        )
        .distinct()
    )

    return render(
        request,
        "admin/horario/crear_horario.html",
        {
            "periodos": periodos,
            "cursos": cursos,
            "docentes": docentes,
            "cursos_por_docente_json": json.dumps(cursos_por_docente),
            "parejas_periodo_curso_json": json.dumps(
                parejas_periodo_curso_con_horario
            ),
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

    # La edición usa el mismo planificador semanal de la creación, cargando
    # las celdas existentes para poder modificarlas, moverlas o eliminarlas.
    if request.method != "POST":
        asignaciones = (
            AsignacionDocente.objects
            .filter(curso=curso, clase__isnull=False)
            .select_related("docente__usuario", "clase")
            .order_by("docente__usuario__first_name", "docente__usuario__last_name", "clase__titulo")
        )
        docentes_ids = asignaciones.values_list("docente_id", flat=True).distinct()
        docentes = list(
            Docente.objects.filter(id__in=docentes_ids)
            .select_related("usuario")
            .order_by("usuario__first_name", "usuario__last_name")
        )
        clases_por_docente = {}
        for asignacion in asignaciones:
            clases = clases_por_docente.setdefault(str(asignacion.docente_id), [])
            if not any(clase["id"] == asignacion.clase_id for clase in clases):
                clases.append({"id": asignacion.clase_id, "titulo": asignacion.clase.titulo})

        clases_curso = list(curso.clases.values("id", "titulo").order_by("titulo"))
        horarios_iniciales = {}
        for horario in horarios_queryset:
            clave = "_".join((horario.dia, horario.jornada, horario.hora_inicio.strftime("%H:%M"), horario.hora_fin.strftime("%H:%M")))
            horarios_iniciales[clave] = {
                "id": horario.id,
                "periodo": periodo.id,
                "curso": curso.id,
                "docente": horario.docente_id,
                "clase": horario.clase_id,
                "dia": horario.dia,
                "jornada": horario.jornada,
                "horaInicio": horario.hora_inicio.strftime("%H:%M"),
                "horaFin": horario.hora_fin.strftime("%H:%M"),
                "docenteNombreCache": str(horario.docente),
                "claseNombreCache": str(horario.clase) if horario.clase_id else "Materia sin asignar",
                "color": "#639ef1",
            }

        return render(
            request,
            "admin/horario/editar_horario.html",
            {
                "modo_edicion": True,
                "periodo": periodo,
                "curso": curso,
                "docentes": docentes,
                "clases_curso_json": json.dumps(clases_curso),
                "clases_por_docente_json": json.dumps(clases_por_docente),
                "horarios_iniciales_json": json.dumps(horarios_iniciales),
                "celdas_ocupadas_json": "[]",
                "dias": [("lunes", "Lunes"), ("martes", "Martes"), ("miercoles", "Miércoles"), ("jueves", "Jueves"), ("viernes", "Viernes")],
                "horas_manana": [("06:00", "07:00"), ("07:00", "08:00"), ("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00")],
                "horas_tarde": [("12:30", "13:30"), ("13:30", "14:30"), ("14:30", "15:30"), ("15:30", "16:30"), ("16:30", "17:00")],
            },
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
    # Ambas rutas de listado usan el mismo template. Delegar en la vista que
    # serializa ``horarios_data`` evita que el planificador reciba ``null`` y
    # que su JavaScript deje de renderizar los horarios.
    return listar_horarios(request)


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
    # ASIGNACIONES DOCENTE -> CLASE (PARA FILTRADO)
    #
    # Para cada docente, obtenemos la lista de IDs de clases
    # que tiene asignadas en este curso. Con esto, en el
    # frontend podremos filtrar el select de materias
    # cuando el usuario seleccione un docente.
    # =====================================================

    asignaciones_qs = (
        AsignacionDocente.objects
        .filter(
            curso=curso
        )
        .select_related(
            "docente__usuario",
            "clase",
        )
        .order_by(
            "docente__usuario__first_name",
            "docente__usuario__last_name",
            "clase__titulo",
        )
    )

    # Docentes que tienen al menos UNA asignación en este curso.
    # Mostraremos SOLAMENTE estos docentes en el select,
    # para que no aparezcan docentes sin materia asignada.
    docentes_ids = list(
        asignaciones_qs.values_list(
            "docente_id",
            flat=True,
        )
        .distinct()
    )

    docentes = (
        Docente.objects
        .filter(id__in=docentes_ids)
        .select_related("usuario")
        .order_by(
            "usuario__first_name",
            "usuario__last_name",
        )
    )

    # Estructura: { "docente_id": [ { "id": clase_id, "titulo": "..." }, ... ] }
    clases_por_docente = {}

    for asignacion in asignaciones_qs:

        if not asignacion.clase_id:
            continue

        docente_key = str(asignacion.docente_id)

        if docente_key not in clases_por_docente:
            clases_por_docente[docente_key] = []

        ya_existe = any(
            c["id"] == asignacion.clase_id
            for c in clases_por_docente[docente_key]
        )

        if not ya_existe:
            clases_por_docente[docente_key].append({
                "id": asignacion.clase_id,
                "titulo": str(asignacion.clase.titulo),
            })

    # Listado de TODAS las clases (materias) del curso,
    # se usa como fallback si algún docente no tiene
    # materias asignadas específicas.
    clases_curso = list(
        curso.clases.values(
            "id",
            "titulo",
        )
        .order_by("titulo")
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
            "docentes": docentes,
            "clases_curso_json": json.dumps(clases_curso),
            "clases_por_docente_json": json.dumps(clases_por_docente),
            "docente_inicial": str(request.GET.get("docente", "")) if str(request.GET.get("docente", "")) in {str(docente_id) for docente_id in docentes_ids} else "",
            "dias": dias,
            "horas_manana": horas_manana,
            "horas_tarde": horas_tarde,
        },
    )


# ============================================================
# CREAR HORARIO CON ENFOQUE EN DOCENTE
# ============================================================

def crear_horario_docente(request, periodo_id, docente_id, curso_id):
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    docente = get_object_or_404(Docente.objects.select_related("usuario"), pk=docente_id)
    curso = get_object_or_404(Cursos, pk=curso_id)

    asignaciones = list(
        AsignacionDocente.objects
        .filter(curso__isnull=False, docente__isnull=False, clase__isnull=False)
        .select_related("docente__usuario", "curso", "clase")
        .order_by("docente__usuario__first_name", "docente__usuario__last_name", "curso__nombre", "clase__titulo")
    )
    pares_docente_curso = {
        (asignacion.docente_id, asignacion.curso_id)
        for asignacion in asignaciones
    }
    if (docente.id, curso.id) not in pares_docente_curso:
        messages.error(request, "El docente no tiene asignaciones en el curso seleccionado.")
        return redirect("crear_horario")

    docentes_por_id = {}
    cursos_por_id = {}
    cursos_por_docente = {}
    clases_por_docente = {}
    for asignacion in asignaciones:
        docentes_por_id[asignacion.docente_id] = asignacion.docente
        cursos_por_id[asignacion.curso_id] = asignacion.curso
        cursos_por_docente.setdefault(str(asignacion.docente_id), {})[asignacion.curso_id] = asignacion.curso.nombre
        if asignacion.clase_id:
            clases_por_docente.setdefault(str(asignacion.docente_id), {}).setdefault(asignacion.curso_id, {})[asignacion.clase_id] = asignacion.clase.titulo

    clases_actuales = clases_por_docente.get(str(docente.id), {}).get(curso.id, {})
    horarios_actuales = Horario.objects.filter(
        periodo=periodo, curso=curso, docente=docente
    ).select_related("clase")
    horarios_iniciales = {}
    for horario in horarios_actuales:
        clave = "_".join((horario.dia, horario.jornada, horario.hora_inicio.strftime("%H:%M"), horario.hora_fin.strftime("%H:%M")))
        horarios_iniciales[clave] = {
            "id": horario.id,
            "periodo": periodo.id,
            "curso": curso.id,
            "docente": docente.id,
            "clase": horario.clase_id,
            "dia": horario.dia,
            "jornada": horario.jornada,
            "horaInicio": horario.hora_inicio.strftime("%H:%M"),
            "horaFin": horario.hora_fin.strftime("%H:%M"),
            "docenteNombreCache": str(docente),
            "claseNombreCache": str(horario.clase) if horario.clase_id else "Materia sin asignar",
            "color": "#639ef1",
        }

    horarios_ocupados = Horario.objects.filter(
        periodo=periodo, curso=curso
    ).exclude(docente=docente).values_list("dia", "jornada", "hora_inicio", "hora_fin")
    celdas_ocupadas = [
        "_".join((dia, jornada, hora_inicio.strftime("%H:%M"), hora_fin.strftime("%H:%M")))
        for dia, jornada, hora_inicio, hora_fin in horarios_ocupados
    ]
    clases_curso = [
        {"id": clase_id, "titulo": titulo}
        for clase_id, titulo in clases_actuales.items()
    ]
    clases_por_docente_actual = {str(docente.id): clases_curso}

    return render(
        request,
        "admin/horario/crear_horario_curso.html.html",
        {
            "modo_docente": True,
            "periodo": periodo,
            "curso": curso,
            "docente_actual": docente,
            "docentes_selector": sorted(docentes_por_id.values(), key=lambda item: str(item).casefold()),
            "cursos_selector": sorted(cursos_por_id.values(), key=lambda item: item.nombre.casefold()),
            "cursos_docente_json": json.dumps(cursos_por_docente),
            "docente_curso_seleccion": {"docente": docente.id, "curso": curso.id},
            "docentes": [docente],
            "clases_curso_json": json.dumps(clases_curso),
            "clases_por_docente_json": json.dumps(clases_por_docente_actual),
            "horarios_iniciales_json": json.dumps(horarios_iniciales),
            "celdas_ocupadas_json": json.dumps(celdas_ocupadas),
            "docente_inicial": str(docente.id),
            "dias": [("lunes", "Lunes"), ("martes", "Martes"), ("miercoles", "Miércoles"), ("jueves", "Jueves"), ("viernes", "Viernes")],
            "horas_manana": [("06:00", "07:00"), ("07:00", "08:00"), ("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00")],
            "horas_tarde": [("12:30", "13:30"), ("13:30", "14:30"), ("14:30", "15:30"), ("15:30", "16:30"), ("16:30", "17:00")],
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

        modo_docente = request.POST.get("modo_docente") == "1"
        modo_edicion = request.POST.get("modo_edicion") == "1"
        ids_eliminados = json.loads(request.POST.get("horariosEliminados", "[]")) if (modo_docente or modo_edicion) else []
        if not isinstance(ids_eliminados, list):
            raise ValueError("La lista de horarios eliminados no es válida.")

        datos = request.POST.get("horarios")

        if not datos and not ids_eliminados:

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

        if not horarios_recibidos and not ids_eliminados:

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
        eliminados = 0
        periodos_cursos_creados_en_lote = set()

        # ====================================================
        # TRANSACCIÓN
        # ====================================================

        with transaction.atomic():

            if (modo_docente or modo_edicion) and ids_eliminados:
                periodo_contexto = request.POST.get("periodo")
                curso_contexto = request.POST.get("curso")
                horarios_a_eliminar = Horario.objects.filter(
                    pk__in=ids_eliminados,
                    periodo_id=periodo_contexto,
                    curso_id=curso_contexto,
                )
                if modo_docente:
                    horarios_a_eliminar = horarios_a_eliminar.filter(docente_id=request.POST.get("docente"))
                eliminados = horarios_a_eliminar.delete()[0]

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

                if modo_docente or modo_edicion:
                    if str(periodo_id) != str(request.POST.get("periodo")) or str(curso_id) != str(request.POST.get("curso")):
                        raise ValueError("El horario no corresponde al período y curso seleccionados.")
                if modo_docente:
                    if str(periodo_id) != str(request.POST.get("periodo")) or str(docente_id) != str(request.POST.get("docente")) or str(curso_id) != str(request.POST.get("curso")):
                        raise ValueError("El horario no corresponde al docente y curso seleccionados.")
                    if not AsignacionDocente.objects.filter(docente_id=docente_id, curso_id=curso_id, clase_id=clase_id).exists():
                        raise ValueError("La materia no está asignada a este docente en el curso seleccionado.")

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

                    horario_filtro = {"pk": horario_id}
                    if modo_docente:
                        horario_filtro.update(periodo_id=periodo_id, docente_id=docente_id, curso_id=curso_id)
                    elif modo_edicion:
                        horario_filtro.update(periodo_id=periodo_id, curso_id=curso_id)
                    horario = get_object_or_404(Horario, **horario_filtro)

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
                    # Un curso puede tener muchas celdas de horario por período;
                    # solo se rechaza crear otro horario cuando ya existía antes
                    # de iniciar este lote de guardado.
                    #
                    # Ejemplo:
                    #
                    # Período 1 + Curso 5B -> ya existe
                    #
                    # Las celdas del mismo lote comparten el curso y el período.

                    clave_periodo_curso = (str(periodo_id), str(curso_id))

                    if not modo_docente and not modo_edicion and clave_periodo_curso not in periodos_cursos_creados_en_lote:
                        horario_existente = Horario.objects.filter(
                            periodo_id=periodo_id,
                            curso_id=curso_id
                        ).exists()

                        if horario_existente:
                            raise ValueError(
                                "El curso seleccionado ya tiene un "
                                "horario registrado para este período."
                            )

                        periodos_cursos_creados_en_lote.add(clave_periodo_curso)

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

        elif eliminados:

            mensaje = f"{eliminados} horario(s) eliminado(s) correctamente."

        else:

            mensaje = (
                "No se realizaron cambios."
            )

        messages.success(
            request,
            mensaje
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
