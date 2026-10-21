from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.user.models import Usuario

from apps.docentes.models import (
    Docente,
    AsignacionDocente,
    MAX_CURSOS_POR_DOCENTE,
    MAX_MATERIAS_POR_DOCENTE
)
from apps.docentes.forms import (
    DocenteForm,
    AsignacionDocenteForm,
    EditarDocenteUsuarioForm
)

from apps.tareas.models import (
    Tareas,
    TareaAlumno,
    RespuestaAlumno,
    Pregunta,
    Imagen,
    ArchivoTarea,
    Video,
    RespuestaCorrecta,
    OpcionesRespuesta,
)

from apps.tareas.forms import TareasForm
from apps.tareas.services import Crear_preguntas

from apps.alumnos.models import Alumnos
from apps.cursos.models import Cursos
from apps.clases.models import Clases

from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation


# ============================================================
# ADMINISTRADOR
# ============================================================

def Listar_docentes(request):

    docentes = list(Usuario.objects.filter(
        rol__nombre="docente"
    ).order_by("first_name", "last_name", "username"))

    cursos_por_docente = {docente.id: [] for docente in docentes}
    if cursos_por_docente:
        asignaciones = (
            AsignacionDocente.objects
            .filter(docente__usuario_id__in=cursos_por_docente, curso__isnull=False)
            .select_related("curso", "docente")
            .order_by("curso__nombre")
        )
        for asignacion in asignaciones:
            cursos = cursos_por_docente[asignacion.docente.usuario_id]
            if asignacion.curso.nombre not in cursos:
                cursos.append(asignacion.curso.nombre)

    for docente in docentes:
        docente.cursos_asignados = cursos_por_docente[docente.id]

    return render(
        request,
        "admin/docente/docentes.html",
        {
            "docentes": docentes,
            "docentes_con_cursos": sum(bool(docente.cursos_asignados) for docente in docentes),
            "docentes_sin_cursos": sum(not docente.cursos_asignados for docente in docentes),
        }
    )


def Editar_docente(request, docente_id):
    docente = get_object_or_404(
        Docente,
        usuario_id=docente_id
    )

    usuario = docente.usuario

    asignaciones = (
        AsignacionDocente.objects
        .filter(docente=docente)
        .select_related("curso", "clase")
    )
    cursos_asignados = asignaciones.filter(curso__isnull=False)
    materias_asignaciones = asignaciones.filter(clase__isnull=False)
    cursos_disponibles = Cursos.objects.exclude(
        id__in=cursos_asignados.values_list("curso_id", flat=True)
    ).order_by("nombre")

    # Materias (clases) únicas asignadas al docente
    materias_asignadas = (
        AsignacionDocente.objects
        .filter(
            docente=docente,
            clase__isnull=False
        )
        .values_list("clase_id", flat=True)
        .distinct()
    )
    clases_disponibles = Clases.objects.exclude(id__in=materias_asignadas).order_by("titulo")

    if request.method == "POST":

        # ==========================================================
        # GUARDAR DATOS DEL DOCENTE
        # ==========================================================
        if "guardar_docente" in request.POST:

            usuario_form = EditarDocenteUsuarioForm(
                request.POST,
                instance=usuario
            )

            docente_form = DocenteForm(
                request.POST,
                instance=docente
            )

            asignacion_form = AsignacionDocenteForm()

            if (
                usuario_form.is_valid()
                and docente_form.is_valid()
            ):
                usuario_form.save()
                docente_form.save()

                messages.success(
                    request,
                    "Datos del docente actualizados correctamente."
                )

                return redirect(
                    "editar_docente",
                    docente_id=docente_id
                )

        # ==========================================================
        # POST DESCONOCIDO
        # ==========================================================
        else:

            usuario_form = EditarDocenteUsuarioForm(
                instance=usuario
            )

            docente_form = DocenteForm(
                instance=docente
            )

            asignacion_form = AsignacionDocenteForm()

    else:

        usuario_form = EditarDocenteUsuarioForm(
            instance=usuario
        )

        docente_form = DocenteForm(
            instance=docente
        )

        asignacion_form = AsignacionDocenteForm()

    return render(
        request,
        "admin/docente/editar_docente.html",
        {
            "docente": docente,
            "usuario_form": usuario_form,
            "docente_form": docente_form,
            "asignacion_form": asignacion_form,
            "asignaciones": asignaciones,
            "cursos_asignados": cursos_asignados,
            "cursos_disponibles": cursos_disponibles,
            "materias_asignaciones": materias_asignaciones,
            "clases_disponibles": clases_disponibles,
            "max_asignaciones": MAX_CURSOS_POR_DOCENTE,
            "max_materias": MAX_MATERIAS_POR_DOCENTE,
            "materias_asignadas": materias_asignadas,
        }
    )


# ============================================================
# GUARDAR DATOS DEL DOCENTE VÍA AJAX (SIN RECARGAR)
# ============================================================

@require_POST
def guardar_docente_ajax(request, docente_id):

    docente = get_object_or_404(
        Docente,
        usuario_id=docente_id
    )

    usuario = docente.usuario

    usuario_form = EditarDocenteUsuarioForm(
        request.POST,
        instance=usuario
    )

    docente_form = DocenteForm(
        request.POST,
        instance=docente
    )

    if (
        usuario_form.is_valid()
        and docente_form.is_valid()
    ):

        usuario_form.save()
        docente_form.save()

        return JsonResponse(
            {
                "ok": True,
                "mensaje": "Datos del docente actualizados correctamente.",
            }
        )

    # =====================================================
    # RECOPILAR ERRORES
    # =====================================================

    errores = {}

    for campo, lista_errores in usuario_form.errors.items():

        errores[campo] = [
            str(e)
            for e in lista_errores
        ]

    for campo, lista_errores in docente_form.errors.items():

        errores[campo] = [
            str(e)
            for e in lista_errores
        ]

    return JsonResponse(
        {
            "ok": False,
            "mensaje": "No se pudieron actualizar los datos del docente.",
            "errores": errores,
        },
        status=400
    )


# ============================================================
# ASIGNAR CURSO/MATERIA VÍA AJAX (SIN RECARGAR)
# ============================================================

@require_POST
def asignar_curso_materia_ajax(request, docente_id):

    docente = get_object_or_404(
        Docente,
        usuario_id=docente_id
    )

    tipo = request.POST.get("tipo")
    curso_ids = request.POST.getlist("cursos") or ([request.POST.get("curso")] if request.POST.get("curso") else [])
    clase_id = request.POST.get("clase")

    if tipo == "editar_clase":
        asignacion_id = request.POST.get("asignacion_id")
        nueva_clase_id = request.POST.get("clase")
        if not str(asignacion_id or "").isdigit() or not str(nueva_clase_id or "").isdigit():
            return JsonResponse({"ok": False, "mensaje": "Selecciona una clase válida."}, status=400)
        asignacion = get_object_or_404(
            AsignacionDocente, id=asignacion_id, docente=docente, clase__isnull=False
        )
        clase_nueva = get_object_or_404(Clases, id=nueva_clase_id)
        if AsignacionDocente.objects.filter(docente=docente, clase=clase_nueva).exclude(id=asignacion.id).exists():
            return JsonResponse({"ok": False, "mensaje": "Esa clase ya está asignada a este docente."}, status=400)
        clase_anterior = {"id": asignacion.clase_id, "nombre": asignacion.clase.titulo}
        asignacion.clase = clase_nueva
        asignacion.save(update_fields=["clase"])
        return JsonResponse({
            "ok": True,
            "mensaje": "Asignación de clase actualizada correctamente.",
            "asignacion": {"id": asignacion.id, "tipo": "materia", "clase_id": clase_nueva.id, "clase": clase_nueva.titulo},
            "clase_anterior": clase_anterior,
        })

    if tipo == "clase":
        clase_ids = list(dict.fromkeys(request.POST.getlist("clases")))
        if not clase_ids or any(not str(value).isdigit() for value in clase_ids):
            return JsonResponse({"ok": False, "mensaje": "Selecciona una o más clases válidas."}, status=400)
        ids_enteros = [int(value) for value in clase_ids]
        clases_actuales = set(AsignacionDocente.objects.filter(
            docente=docente, clase__isnull=False
        ).values_list("clase_id", flat=True).distinct())
        ids_nuevos = [clase_id for clase_id in ids_enteros if clase_id not in clases_actuales]
        if not ids_nuevos:
            return JsonResponse({"ok": False, "mensaje": "Las clases seleccionadas ya están asignadas."}, status=400)
        if len(clases_actuales) + len(ids_nuevos) > MAX_MATERIAS_POR_DOCENTE:
            return JsonResponse({
                "ok": False,
                "mensaje": f"Cada docente puede tener máximo {MAX_MATERIAS_POR_DOCENTE} clases asignadas.",
            }, status=400)
        clases_nuevas = list(Clases.objects.filter(id__in=ids_nuevos).order_by("titulo"))
        if len(clases_nuevas) != len(ids_nuevos):
            return JsonResponse({"ok": False, "mensaje": "Una o más clases seleccionadas no existen."}, status=400)
        asignaciones_creadas = [
            AsignacionDocente.objects.create(docente=docente, clase=clase)
            for clase in clases_nuevas
        ]
        return JsonResponse({
            "ok": True,
            "mensaje": "Clases asignadas correctamente.",
            "asignaciones": [
                {"id": asignacion.id, "tipo": "materia", "clase_id": asignacion.clase_id, "clase": asignacion.clase.titulo}
                for asignacion in asignaciones_creadas
            ],
            "materias_count": len(clases_actuales) + len(asignaciones_creadas),
            "max_materias": MAX_MATERIAS_POR_DOCENTE,
        })

    if tipo == "editar_curso":
        asignacion_id = request.POST.get("asignacion_id")
        curso_id = request.POST.get("curso")
        if not str(asignacion_id or "").isdigit() or not str(curso_id or "").isdigit():
            return JsonResponse({"ok": False, "mensaje": "Selecciona un curso válido."}, status=400)
        asignacion = get_object_or_404(
            AsignacionDocente, id=asignacion_id, docente=docente, curso__isnull=False
        )
        curso_nuevo = get_object_or_404(Cursos, id=curso_id)
        if AsignacionDocente.objects.filter(docente=docente, curso=curso_nuevo).exclude(id=asignacion.id).exists():
            return JsonResponse({"ok": False, "mensaje": "Ese curso ya está asignado a este docente."}, status=400)
        curso_anterior = {"id": asignacion.curso_id, "nombre": asignacion.curso.nombre}
        asignacion.curso = curso_nuevo
        asignacion.save(update_fields=["curso"])
        return JsonResponse({
            "ok": True,
            "mensaje": "Asignación de curso actualizada correctamente.",
            "asignacion": {"id": asignacion.id, "tipo": "curso", "curso_id": curso_nuevo.id, "curso": curso_nuevo.nombre},
            "curso_anterior": curso_anterior,
        })

    if tipo not in ("curso", "materia"):
        return JsonResponse({"ok": False, "mensaje": "Selecciona si vas a asignar un curso o una materia."}, status=400)
    if tipo == "curso" and not curso_ids:
        return JsonResponse({"ok": False, "mensaje": "Debes seleccionar un curso."}, status=400)
    if tipo == "materia" and not clase_id:

        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Debes seleccionar una materia."
            },
            status=400
        )

    # =====================================================
    # VALIDAR MÁXIMO DE MATERIAS (3)
    # =====================================================

    materias_actuales = set(
        AsignacionDocente.objects
        .filter(
            docente=docente,
            clase__isnull=False
        )
        .values_list("clase_id", flat=True)
        .distinct()
    )

    if tipo == "materia" and int(clase_id) in materias_actuales:
        return JsonResponse({"ok": False, "mensaje": "Esa materia ya está asignada a este docente."}, status=400)
    nuevos_cursos = []
    if tipo == "curso":
        curso_ids = list(dict.fromkeys(curso_ids))
        if any(not str(curso_id).isdigit() for curso_id in curso_ids):
            return JsonResponse({"ok": False, "mensaje": "La selección contiene un curso no válido."}, status=400)
        cursos_existentes = set(AsignacionDocente.objects.filter(
            docente=docente, curso_id__in=curso_ids
        ).values_list("curso_id", flat=True))
        nuevos_ids = [curso_id for curso_id in curso_ids if int(curso_id) not in cursos_existentes]
        if not nuevos_ids:
            return JsonResponse({"ok": False, "mensaje": "Los cursos seleccionados ya estÃ¡n asignados."}, status=400)
        nuevos_cursos = list(Cursos.objects.filter(id__in=nuevos_ids).order_by("nombre"))
        if len(nuevos_cursos) != len(nuevos_ids):
            return JsonResponse({"ok": False, "mensaje": "Uno o mÃ¡s cursos seleccionados no existen."}, status=400)
        nuevas_asignaciones = [
            AsignacionDocente.objects.create(docente=docente, curso=curso)
            for curso in nuevos_cursos
        ]
        return JsonResponse({
            "ok": True,
            "mensaje": "Cursos asignados correctamente.",
            "asignaciones": [
                {"id": a.id, "tipo": "curso", "curso_id": a.curso_id, "curso": a.curso.nombre, "clase": ""}
                for a in nuevas_asignaciones
            ],
            "materias_count": len(materias_actuales),
            "max_materias": MAX_MATERIAS_POR_DOCENTE,
        })
    if tipo == "materia" and (
        int(clase_id) not in materias_actuales
        and len(materias_actuales) >= MAX_MATERIAS_POR_DOCENTE
    ):

        return JsonResponse(
            {
                "ok": False,
                "mensaje": (
                    f"El docente ya tiene asignadas "
                    f"{MAX_MATERIAS_POR_DOCENTE} materias. "
                    "Debe quitar una materia antes de asignar otra."
                )
            },
            status=400
        )

    # =====================================================
    # CREAR ASIGNACIÓN
    # =====================================================

    asignacion = AsignacionDocente.objects.create(
        docente=docente,
        clase_id=clase_id,
    )

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "Asignación creada correctamente.",
            "asignacion": {
                "id": asignacion.id,
                "tipo": tipo,
                "curso": asignacion.curso.nombre if asignacion.curso else "",
                "clase": (
                    asignacion.clase.titulo
                    if asignacion.clase
                    else ""
                ),
            },
            "materias_count": len(
                set(
                    AsignacionDocente.objects
                    .filter(
                        docente=docente,
                        clase__isnull=False
                    )
                    .values_list("clase_id", flat=True)
                    .distinct()
                )
            ),
            "max_materias": MAX_MATERIAS_POR_DOCENTE,
        }
    )


# ============================================================
# ELIMINAR ASIGNACIÓN VÍA AJAX (SIN RECARGAR)
# ============================================================

@require_POST
def eliminar_asignacion_ajax(request, asignacion_id):

    asignacion = get_object_or_404(
        AsignacionDocente,
        id=asignacion_id
    )

    docente = asignacion.docente

    tipo = request.POST.get("tipo")
    curso_quitado = {"id": asignacion.curso_id, "nombre": asignacion.curso.nombre} if tipo == "curso" and asignacion.curso_id else None
    clase_quitada = {"id": asignacion.clase_id, "nombre": asignacion.clase.titulo} if tipo == "materia" and asignacion.clase_id else None
    if tipo == "materia" and asignacion.curso_id:
        asignacion.clase = None
        asignacion.save(update_fields=["clase"])
    elif tipo == "curso" and asignacion.clase_id:
        asignacion.curso = None
        asignacion.save(update_fields=["curso"])
    else:
        asignacion.delete()

    materias_count = len(
        set(
            AsignacionDocente.objects
            .filter(
                docente=docente,
                clase__isnull=False
            )
            .values_list("clase_id", flat=True)
            .distinct()
        )
    )

    return JsonResponse(
        {
            "ok": True,
            "mensaje": "Asignación eliminada.",
            "materias_count": materias_count,
            "max_materias": MAX_MATERIAS_POR_DOCENTE,
            "curso_quitado": curso_quitado,
            "clase_quitada": clase_quitada,
        }
    )



def Eliminar_asignacion_docente(
    request,
    asignacion_id
):

    asignacion = get_object_or_404(
        AsignacionDocente,
        id=asignacion_id
    )

    docente_id = asignacion.docente.usuario_id

    if request.method == "POST":

        asignacion.delete()

        messages.success(
            request,
            "Asignación eliminada."
        )

    return redirect(
        "editar_docente",
        docente_id=docente_id
    )


def Eliminar_docente(
    request,
    docente_id
):

    docente = get_object_or_404(
        Docente,
        usuario_id=docente_id
    )

    if request.method == "POST":

        nombre_docente = docente.usuario.get_full_name() or docente.usuario.documento
        docente.usuario.delete()
        messages.success(request, f"Docente {nombre_docente} eliminado correctamente.")

        return redirect(
            "listar_docentes"
        )

    return render(
        request,
        "admin/docente/eliminar_docente.html",
        {
            "docente": docente
        }
    )


# ============================================================
# CREAR TAREA
# ============================================================

def crear_tareas_docente(request):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # ASIGNACIONES DEL DOCENTE
    # =========================================================

    asignaciones = (
        AsignacionDocente.objects
        .filter(docente=docente)
        .select_related(
            "docente",
            "curso"
        )
    )

    # Cursos únicos del docente
    cursos = []

    for asignacion in asignaciones:

        curso = asignacion.curso

        if curso and curso not in cursos:
            cursos.append(curso)

    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        tarea_form = TareasForm(
            request.POST,
            request.FILES
        )

        asignacion_id = request.POST.get("asignacion")

        if not asignacion_id:

            messages.error(
                request,
                "Debes seleccionar una materia y un curso."
            )

        else:

            # =================================================
            # BUSCAR ASIGNACIÓN DEL DOCENTE
            # =================================================

            asignacion = (
                AsignacionDocente.objects
                .filter(
                    docente=docente,
                    id=asignacion_id
                )
                .select_related(
                    "curso",
                    "clase"
                )
                .first()
            )

            if not asignacion:

                messages.error(
                    request,
                    "No tienes ese curso asignado."
                )

            elif tarea_form.is_valid():

                with transaction.atomic():

                    # =========================================
                    # CREAR TAREA
                    # =========================================

                    tarea = tarea_form.save(
                        commit=False
                    )

                    tarea.docente = docente
                    tarea.curso = asignacion.curso
                    tarea.clase = asignacion.clase

                    tarea.save()

                    # =========================================
                    # IMÁGENES
                    # =========================================

                    for imagen in request.FILES.getlist(
                        "imagenes"
                    ):

                        Imagen.objects.create(
                            tarea=tarea,
                            imagen=imagen
                        )

                    # =========================================
                    # ARCHIVOS
                    # =========================================

                    for archivo in request.FILES.getlist(
                        "archivos"
                    ):

                        ArchivoTarea.objects.create(
                            tarea=tarea,
                            archivo=archivo
                        )

                    # =========================================
                    # VIDEOS
                    # =========================================

                    for video in request.POST.getlist(
                        "videos"
                    ):

                        video = video.strip()

                        if video:

                            Video.objects.create(
                                tarea=tarea,
                                video=video
                            )

                    # =========================================
                    # PREGUNTAS
                    # =========================================

                    Crear_preguntas(
                        request,
                        tarea
                    )

                messages.success(
                    request,
                    "La tarea fue creada correctamente."
                )

                return redirect(
                    "listar_tareas_docentes"
                )

    else:

        tarea_form = TareasForm()

    return render(
        request,
        "paneles/docentes/tareas/crear_tarea.html",
        {
            "tarea_form": tarea_form,
            "docente": docente,
            "cursos": cursos,
            "asignaciones": asignaciones,
        }
    )


# ============================================================
# EDITAR TAREA
# ============================================================

def editar_tarea_docente(
    request,
    tarea_id
):

    # =========================================================
    # OBTENER DOCENTE
    # =========================================================

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # OBTENER TAREA
    # =========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    # =========================================================
    # ASIGNACIONES DEL DOCENTE
    # =========================================================

    asignaciones = (
        AsignacionDocente.objects
        .filter(
            docente=docente
        )
        .select_related(
            "docente",
            "curso"
        )
    )

    # =========================================================
    # CURSOS DISPONIBLES
    # =========================================================

    cursos = []

    for asignacion in asignaciones:

        curso = asignacion.curso

        if curso and curso not in cursos:
            cursos.append(curso)

    # =========================================================
    # POST
    # =========================================================

    if request.method == "POST":

        tarea_form = TareasForm(
            request.POST,
            request.FILES,
            instance=tarea
        )

        curso_id = request.POST.get(
            "curso"
        )

        if not curso_id:

            messages.error(
                request,
                "Debes seleccionar un curso."
            )

        else:

            # =================================================
            # BUSCAR ASIGNACIÓN
            # =================================================

            asignacion = (
                AsignacionDocente.objects
                .filter(
                    docente=docente,
                    curso_id=curso_id,
                    clase_id=request.POST.get("clase") or None,
                )
                .select_related(
                    "docente",
                    "curso",
                    "clase",
                )
                .first()
            )

            if not asignacion:

                messages.error(
                    request,
                    "No puedes asignar esta tarea a ese curso."
                )

            elif tarea_form.is_valid():

                try:

                    with transaction.atomic():

                        # =====================================
                        # ACTUALIZAR TAREA
                        # =====================================

                        tarea_editada = tarea_form.save(
                            commit=False
                        )

                        tarea_editada.docente = docente

                        # La asignación ahora es por CURSO
                        tarea_editada.curso = (
                            asignacion.curso
                        )
                        tarea_editada.clase = asignacion.clase

                        tarea_editada.save()

                        # =====================================
                        # IMÁGENES NUEVAS
                        # =====================================

                        for imagen in request.FILES.getlist(
                            "imagenes"
                        ):

                            Imagen.objects.create(
                                tarea=tarea_editada,
                                imagen=imagen
                            )

                        # =====================================
                        # ARCHIVOS NUEVOS
                        # =====================================

                        for archivo in request.FILES.getlist(
                            "archivos"
                        ):

                            ArchivoTarea.objects.create(
                                tarea=tarea_editada,
                                archivo=archivo
                            )

                        # =====================================
                        # VIDEOS NUEVOS
                        # =====================================

                        for video_url in request.POST.getlist(
                            "videos"
                        ):

                            video_url = video_url.strip()

                            if video_url:

                                Video.objects.create(
                                    tarea=tarea_editada,
                                    video=video_url
                                )

                        # =====================================
                        # OBTENER ÍNDICES DE PREGUNTAS
                        # =====================================

                        indices = []

                        for key in request.POST.keys():

                            if key.startswith(
                                "pregunta_"
                            ):

                                try:

                                    indice = int(
                                        key.split("_")[1]
                                    )

                                    indices.append(
                                        indice
                                    )

                                except (
                                    ValueError,
                                    IndexError
                                ):

                                    continue

                        indices = sorted(
                            set(indices)
                        )

                        # =====================================
                        # PROCESAR PREGUNTAS
                        # =====================================

                        for indice in indices:

                            enunciado = request.POST.get(
                                f"pregunta_{indice}"
                            )

                            tipo = request.POST.get(
                                f"tipo_{indice}"
                            )

                            puntaje = request.POST.get(
                                f"puntaje_{indice}"
                            )

                            pregunta_id = request.POST.get(
                                f"pregunta_id_{indice}"
                            )

                            if not enunciado:
                                continue

                            # =================================
                            # PREGUNTA EXISTENTE
                            # =================================

                            if pregunta_id:

                                pregunta = get_object_or_404(
                                    Pregunta,
                                    id=pregunta_id,
                                    tarea=tarea_editada
                                )

                                pregunta.descripcion = (
                                    enunciado
                                )

                                pregunta.tipo = tipo

                                if puntaje:

                                    pregunta.puntaje = (
                                        puntaje
                                    )

                                pregunta.save()

                            # =================================
                            # PREGUNTA NUEVA
                            # =================================

                            else:

                                pregunta = (
                                    Pregunta.objects.create(
                                        tarea=tarea_editada,
                                        descripcion=enunciado,
                                        tipo=tipo,
                                        puntaje=(
                                            puntaje
                                            if puntaje
                                            else 1
                                        )
                                    )
                                )

                            # =================================
                            # RESPUESTA ABIERTA
                            # =================================

                            if tipo == "texto":

                                respuesta = request.POST.get(
                                    f"respuesta_correcta_{indice}"
                                )

                                if respuesta:

                                    RespuestaCorrecta.objects.update_or_create(
                                        pregunta=pregunta,
                                        defaults={
                                            "respuesta": respuesta
                                        }
                                    )

                                else:

                                    RespuestaCorrecta.objects.filter(
                                        pregunta=pregunta
                                    ).delete()

                                OpcionesRespuesta.objects.filter(
                                    pregunta=pregunta
                                ).update(
                                    es_correcta=False
                                )

                            # =================================
                            # OPCIÓN MÚLTIPLE
                            # =================================

                            elif tipo == "opcion":

                                RespuestaCorrecta.objects.filter(
                                    pregunta=pregunta
                                ).delete()

                                opciones = request.POST.getlist(
                                    f"opciones_{indice}[]"
                                )

                                correcta = request.POST.get(
                                    f"correcta_{indice}"
                                )

                                letras = [
                                    "A",
                                    "B",
                                    "C",
                                    "D"
                                ]

                                opciones_existentes = list(
                                    pregunta.opciones.all()
                                )

                                for i, texto_opcion in enumerate(
                                    opciones
                                ):

                                    if i >= len(letras):
                                        break

                                    texto_opcion = (
                                        texto_opcion.strip()
                                    )

                                    if not texto_opcion:
                                        continue

                                    es_correcta = (
                                        letras[i] == correcta
                                    )

                                    if i < len(
                                        opciones_existentes
                                    ):

                                        opcion = (
                                            opciones_existentes[i]
                                        )

                                        opcion.opcion = (
                                            texto_opcion
                                        )

                                        opcion.es_correcta = (
                                            es_correcta
                                        )

                                        opcion.save()

                                    else:

                                        OpcionesRespuesta.objects.create(
                                            pregunta=pregunta,
                                            opcion=texto_opcion,
                                            es_correcta=es_correcta
                                        )

                    messages.success(
                        request,
                        "La tarea fue actualizada correctamente."
                    )

                    return redirect(
                        "listar_tareas_docentes"
                    )

                except Exception as e:

                    messages.error(
                        request,
                        f"No se pudo actualizar la tarea: {e}"
                    )

            else:

                messages.error(
                    request,
                    "Revisa los datos del formulario."
                )

    else:

        tarea_form = TareasForm(
            instance=tarea
        )

    # =========================================================
    # PREGUNTAS
    # =========================================================

    preguntas = (
        tarea.preguntas
        .prefetch_related(
            "opciones"
        )
        .all()
    )

    # =========================================================
    # CURSO ACTUAL
    # =========================================================

    curso_actual = tarea.curso

    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "paneles/docentes/tareas/editar_tarea.html",
        {
            "tarea": tarea,
            "tarea_form": tarea_form,
            "preguntas": preguntas,
            "cursos": cursos,
            "curso_actual": curso_actual,
            "docente": docente,
        }
    )


# ============================================================
# ELIMINAR TAREA
# ============================================================

def eliminar_tarea_docente(
    request,
    tarea_id
):

    # =========================================================
    # OBTENER DOCENTE
    # =========================================================

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # OBTENER TAREA DEL DOCENTE
    # =========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    # =========================================================
    # ELIMINAR
    # =========================================================

    if request.method == "POST":

        tarea.delete()

        messages.success(
            request,
            "La tarea fue eliminada correctamente."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # =========================================================
    # CONFIRMACIÓN SI SE ACCEDE POR GET
    # =========================================================

    return render(
        request,
        "paneles/docentes/tareas/eliminar_tarea.html",
        {
            "tarea": tarea
        }
    )


# ============================================================
# LISTAR TAREAS DEL DOCENTE
# ============================================================

def listar_tareas(request):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # TAREAS DEL DOCENTE
    # =========================================================

    tareas = (
        Tareas.objects
        .filter(
            docente=docente
        )
        .order_by(
            "-fecha_creacion"
        )
    )

    # =========================================================
    # CURSOS ASIGNADOS AL DOCENTE
    # =========================================================

    asignaciones = (
        AsignacionDocente.objects
        .filter(
            docente=docente
        )
        .select_related(
            "docente",
            "curso"
        )
    )

    # AsignacionDocente ahora tiene directamente el campo curso
    cursos_ids = [
        asignacion.curso_id
        for asignacion in asignaciones
        if asignacion.curso_id
    ]

    # Eliminar cursos duplicados
    cursos_ids = list(
        set(cursos_ids)
    )

    # =========================================================
    # TOTAL DE ALUMNOS
    # =========================================================
    #
    # Se cuentan los alumnos de TODOS los cursos
    # asignados al docente.
    # =========================================================

    total_alumnos = (
        Alumnos.objects
        .filter(
            curso_id__in=cursos_ids
        )
        .count()
        if cursos_ids
        else 0
    )

    # =========================================================
    # ESTADÍSTICAS DE CADA TAREA
    # =========================================================

    for tarea in tareas:

        # -----------------------------------------------------
        # Total de alumnos del curso de ESTA tarea
        # -----------------------------------------------------

        if tarea.curso_id:

            total_alumnos_tarea = (
                Alumnos.objects
                .filter(
                    curso_id=tarea.curso_id
                )
                .count()
            )

        else:

            total_alumnos_tarea = 0

        tarea.total_alumnos = (
            total_alumnos_tarea
        )

        # -----------------------------------------------------
        # Entregas
        # -----------------------------------------------------

        tarea.entregas = (
            RespuestaAlumno.objects
            .filter(
                pregunta__tarea=tarea
            )
            .values(
                "alumno"
            )
            .distinct()
            .count()
        )

        # -----------------------------------------------------
        # Porcentaje de entrega
        # -----------------------------------------------------

        if total_alumnos_tarea > 0:

            tarea.porcentaje_entrega = (
                tarea.entregas
                / total_alumnos_tarea
            ) * 100

        else:

            tarea.porcentaje_entrega = 0

    # =========================================================
    # CONTADORES
    # =========================================================

    total_tareas = (
        tareas.count()
    )

    tareas_activas = (
        tareas
        .filter(
            activa=True
        )
        .count()
    )

    tareas_sin_fecha = (
        tareas
        .filter(
            fecha_entrega__isnull=True
        )
        .count()
    )

    # =========================================================
    # CONTEXTO
    # =========================================================

    context = {
        "docente": docente,
        "tareas": tareas,
        "total_tareas": total_tareas,
        "tareas_activas": tareas_activas,
        "tareas_sin_fecha": tareas_sin_fecha,
        "total_alumnos": total_alumnos,
    }

    return render(
        request,
        "paneles/docentes/tareas/docente_tareas.html",
        context
    )


# ============================================================
# HABILITAR / DESHABILITAR TAREA
# ============================================================

def habilitar_deshabilitar_tarea(
    request,
    tarea_id
):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # La tarea debe pertenecer al docente

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    # =========================================================
    # SOLO POST
    # =========================================================

    if request.method == "POST":

        tarea.activa = not tarea.activa

        tarea.save(
            update_fields=[
                "activa"
            ]
        )

        if tarea.activa:

            messages.success(
                request,
                "La tarea ha sido habilitada."
            )

        else:

            messages.success(
                request,
                "La tarea ha sido deshabilitada."
            )

    return redirect(
        "listar_tareas_docentes"
    )


# ============================================================
# RESPUESTAS DE ALUMNOS
# ============================================================

def respuesta_alumnos(
    request,
    tarea_id
):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # SOLO TAREAS DEL DOCENTE
    # =========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    alumnos_ids = (
        RespuestaAlumno.objects
        .filter(
            pregunta__tarea=tarea
        )
        .values_list(
            "alumno_id",
            flat=True
        )
        .distinct()
    )

    alumnos = Usuario.objects.filter(
        id__in=alumnos_ids
    )

    # =========================================================
    # ESTADO INDIVIDUAL
    # =========================================================

    estados = (
        TareaAlumno.objects
        .filter(
            tarea=tarea,
            alumno_id__in=alumnos_ids
        )
    )

    estados_dict = {
        estado.alumno_id: estado
        for estado in estados
    }

    alumnos_data = []

    for alumno in alumnos:

        estado = estados_dict.get(
            alumno.id
        )

        activa = (
            estado.activa
            if estado
            else True
        )

        alumnos_data.append(
            {
                "alumno": alumno,
                "activa": activa,
            }
        )

    return render(
        request,
        "paneles/docentes/tareas/respuesta_alumnos.html",
        {
            "tarea": tarea,
            "alumnos": alumnos_data,
        }
    )


# ============================================================
# HABILITAR / DESHABILITAR TAREA PARA ALUMNO
# ============================================================

def habilitar_deshabilitar_tarea_alumno(
    request,
    tarea_id,
    alumno_id
):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    tarea_alumno, creado = (
        TareaAlumno.objects.get_or_create(
            tarea=tarea,
            alumno=alumno
        )
    )

    tarea_alumno.activa = (
        not tarea_alumno.activa
    )

    tarea_alumno.save()

    if tarea_alumno.activa:

        messages.success(
            request,
            f"La tarea fue habilitada para {alumno.get_full_name() or alumno.username}."
        )

    else:

        messages.success(
            request,
            f"La tarea fue deshabilitada para {alumno.get_full_name() or alumno.username}."
        )

    return redirect(
        "respuesta_alumnos",
        tarea_id=tarea.id
    )


# ============================================================
# REPETIR TAREA PARA ALUMNO
# ============================================================

def repetir_tarea_alumno(
    request,
    tarea_id,
    alumno_id
):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    # =========================================================
    # ELIMINAR RESPUESTAS DEL ALUMNO
    # =========================================================

    RespuestaAlumno.objects.filter(
        alumno=alumno,
        pregunta__tarea=tarea
    ).delete()

    # =========================================================
    # REACTIVAR TAREA
    # =========================================================

    tarea_alumno, created = (
        TareaAlumno.objects.get_or_create(
            tarea=tarea,
            alumno=alumno
        )
    )

    tarea_alumno.activa = True

    tarea_alumno.save()

    messages.success(
        request,
        f"La tarea fue reiniciada para {alumno.get_full_name() or alumno.username}."
    )

    return redirect(
        "respuesta_alumnos",
        tarea_id=tarea.id
    )

def ver_respuestas(request, tarea_id, alumno_id):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # VERIFICAR QUE LA TAREA PERTENEZCA AL DOCENTE
    # =========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    # =========================================================
    # OBTENER ALUMNO
    # =========================================================

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    # =========================================================
    # GUARDAR EVALUACIÓN
    # =========================================================

    if request.method == "POST":

        respuesta_id = request.POST.get("respuesta_id")
        estado = request.POST.get("estado")
        nota = request.POST.get("nota")

        # -----------------------------------------------------
        # BUSCAR RESPUESTA
        # -----------------------------------------------------

        respuesta = get_object_or_404(
            RespuestaAlumno,
            id=respuesta_id,
            alumno=alumno,
            pregunta__tarea=tarea
        )

        # -----------------------------------------------------
        # CONVERTIR NOTA
        # -----------------------------------------------------

        try:
            nota = Decimal(nota)
        except (TypeError, ValueError, InvalidOperation):
            nota = Decimal("0")

        # -----------------------------------------------------
        # PUNTAJE MÁXIMO DE LA PREGUNTA
        # -----------------------------------------------------

        puntaje_maximo = respuesta.pregunta.puntaje

        # Evitar valores negativos
        if nota < Decimal("0"):
            nota = Decimal("0")

        # Evitar superar el puntaje máximo
        if nota > puntaje_maximo:
            nota = puntaje_maximo

        # =====================================================
        # CORRECTA
        # =====================================================

        if estado == "correct":

            respuesta.calificada = True
            respuesta.es_correcta = True
            respuesta.nota_obtenida = puntaje_maximo

        # =====================================================
        # INCORRECTA
        # =====================================================

        elif estado == "incorrect":

            respuesta.calificada = True
            respuesta.es_correcta = False
            respuesta.nota_obtenida = Decimal("0")

        # =====================================================
        # PARCIAL
        # =====================================================

        elif estado == "partial":

            respuesta.calificada = True
            respuesta.es_correcta = False
            respuesta.nota_obtenida = nota

        # =====================================================
        # PENDIENTE
        # =====================================================

        elif estado == "pending":

            respuesta.calificada = False
            respuesta.es_correcta = False
            respuesta.nota_obtenida = Decimal("0")

        # =====================================================
        # ESTADO DESCONOCIDO
        # =====================================================

        else:

            respuesta.calificada = False
            respuesta.es_correcta = False
            respuesta.nota_obtenida = Decimal("0")

        # =====================================================
        # GUARDAR EN BASE DE DATOS
        # =====================================================

        respuesta.save()

        # =====================================================
        # VOLVER AL LISTADO DE ESTUDIANTES
        # =====================================================

        return redirect(
            "respuesta_alumnos",
            tarea_id=tarea.id
        )

    # =========================================================
    # OBTENER TODAS LAS PREGUNTAS
    # =========================================================

    preguntas = (
        Pregunta.objects
        .filter(
            tarea=tarea
        )
        .prefetch_related(
            "opciones"
        )
        .order_by("id")
    )

    # =========================================================
    # OBTENER RESPUESTAS DEL ALUMNO
    # =========================================================

    respuestas = (
        RespuestaAlumno.objects
        .filter(
            alumno=alumno,
            pregunta__tarea=tarea
        )
        .select_related(
            "pregunta",
            "opcion_seleccionada"
        )
    )

    # =========================================================
    # CREAR DICCIONARIO
    # =========================================================

    respuestas_dict = {
        respuesta.pregunta_id: respuesta
        for respuesta in respuestas
    }

    # =========================================================
    # RELACIONAR PREGUNTAS CON RESPUESTAS
    # =========================================================

    preguntas_respuestas = []

    for pregunta in preguntas:

        respuesta = respuestas_dict.get(
            pregunta.id
        )

        preguntas_respuestas.append(
            {
                "pregunta": pregunta,
                "respuesta": respuesta
            }
        )

    # =========================================================
    # TOTAL DE PREGUNTAS
    # =========================================================

    total_preguntas = preguntas.count()

    # =========================================================
    # PUNTOS TOTALES
    # =========================================================

    puntos_totales = sum(
        (
            pregunta.puntaje
            for pregunta in preguntas
        ),
        Decimal("0")
    )

    # =========================================================
    # PUNTOS OBTENIDOS
    # =========================================================

    puntos_obtenidos = sum(
        (
            respuesta.nota_obtenida
            for respuesta in respuestas
        ),
        Decimal("0")
    )

    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "paneles/docentes/tareas/ver_respuesta.html",
        {
            "tarea": tarea,
            "alumno": alumno,

            "respuestas": respuestas,

            "preguntas_respuestas": preguntas_respuestas,

            "total_preguntas": total_preguntas,

            "puntos_obtenidos": puntos_obtenidos,

            "puntos_totales": puntos_totales,
        }
    )

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =========================================================
    # VERIFICAR QUE LA TAREA PERTENEZCA AL DOCENTE
    # =========================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id,
        docente=docente
    )

    # =========================================================
    # OBTENER ALUMNO
    # =========================================================

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    # =========================================================
    # GUARDAR EVALUACIÓN
    # =========================================================

    if request.method == "POST":

        respuesta_id = request.POST.get("respuesta_id")
        estado = request.POST.get("estado")
        nota = request.POST.get("nota")

        respuesta = get_object_or_404(
            RespuestaAlumno,
            id=respuesta_id,
            alumno=alumno,
            pregunta__tarea=tarea
        )

        # -----------------------------------------------------
        # CONVERTIR NOTA
        # -----------------------------------------------------

        try:
            nota = Decimal(nota)
        except (TypeError, ValueError, InvalidOperation):
            nota = Decimal("0")

        # -----------------------------------------------------
        # PUNTAJE MÁXIMO DE LA PREGUNTA
        # -----------------------------------------------------

        puntaje_maximo = respuesta.pregunta.puntaje

        if nota < 0:
            nota = Decimal("0")

        if nota > puntaje_maximo:
            nota = puntaje_maximo

        # -----------------------------------------------------
        # CORRECTA
        # -----------------------------------------------------

        if estado == "correct":

            respuesta.calificada = True
            respuesta.es_correcta = True
            respuesta.nota_obtenida = puntaje_maximo

        # -----------------------------------------------------
        # INCORRECTA
        # -----------------------------------------------------

        elif estado == "incorrect":

            respuesta.calificada = True
            respuesta.es_correcta = False
            respuesta.nota_obtenida = Decimal("0")

        # -----------------------------------------------------
        # PARCIAL
        # -----------------------------------------------------

        elif estado == "partial":

            respuesta.calificada = True
            respuesta.es_correcta = False
            respuesta.nota_obtenida = nota

        # -----------------------------------------------------
        # PENDIENTE
        # -----------------------------------------------------

        elif estado == "pending":

            respuesta.calificada = False
            respuesta.es_correcta = False
            respuesta.nota_obtenida = Decimal("0")

        # -----------------------------------------------------
        # GUARDAR
        # -----------------------------------------------------

        respuesta.save()

        # =====================================================
        # VOLVER A LA MISMA PÁGINA
        # =====================================================

        return redirect(
            "ver_respuestas",
            tarea_id=tarea.id,
            alumno_id=alumno.id
        )

    # =========================================================
    # OBTENER PREGUNTAS
    # =========================================================

    preguntas = (
        Pregunta.objects
        .filter(tarea=tarea)
        .prefetch_related("opciones")
        .order_by("id")
    )

    # =========================================================
    # OBTENER RESPUESTAS DEL ALUMNO
    # =========================================================

    respuestas = (
        RespuestaAlumno.objects
        .filter(
            alumno=alumno,
            pregunta__tarea=tarea
        )
        .select_related(
            "pregunta",
            "opcion_seleccionada"
        )
    )

    # =========================================================
    # DICCIONARIO DE RESPUESTAS
    # =========================================================

    respuestas_dict = {
        respuesta.pregunta_id: respuesta
        for respuesta in respuestas
    }

    # =========================================================
    # PREGUNTAS + RESPUESTAS
    # =========================================================

    preguntas_respuestas = []

    for pregunta in preguntas:

        respuesta = respuestas_dict.get(
            pregunta.id
        )

        preguntas_respuestas.append(
            {
                "pregunta": pregunta,
                "respuesta": respuesta,
            }
        )

    # =========================================================
    # TOTALES
    # =========================================================

    total_preguntas = preguntas.count()

    puntos_totales = sum(
        (
            pregunta.puntaje
            for pregunta in preguntas
        ),
        Decimal("0")
    )

    puntos_obtenidos = sum(
        (
            respuesta.nota_obtenida
            for respuesta in respuestas
        ),
        Decimal("0")
    )

    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "paneles/docentes/tareas/ver_respuesta.html",
        {
            "tarea": tarea,
            "alumno": alumno,
            "respuestas": respuestas,
            "preguntas_respuestas": preguntas_respuestas,
            "total_preguntas": total_preguntas,
            "puntos_obtenidos": puntos_obtenidos,
            "puntos_totales": puntos_totales,
        }
    )


def calendario(request):
    return render(
            request,
            "admin/horario/calendario.html"
        )
