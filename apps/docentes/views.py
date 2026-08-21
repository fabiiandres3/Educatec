from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from apps.user.models import Usuario
from apps.user.forms import EditarUsuarioForm
from apps.docentes.models import Docente
from apps.docentes.forms import DocenteForm
from apps.tareas.models import Tareas, RespuestaAlumno, Pregunta
from apps.tareas.forms import TareasForm
from apps.alumnos.models import Alumnos
from apps.cursos.models import Cursos
from apps.tareas.services import Crear_preguntas

#Administrador
def Listar_docentes(request):
    docentes = Usuario.objects.filter(rol__nombre="docente")

    return render(request, "admin/docente/docentes.html", {"docentes": docentes})


def Editar_docente(request, docente_id):
    docente = get_object_or_404(Docente, usuario_id=docente_id)
    usuario = docente.usuario

    if request.method == "POST":
        usuario_form = EditarUsuarioForm(request.POST, instance=usuario)
        docente_form = DocenteForm(request.POST, instance=docente)

        if usuario_form.is_valid() and docente_form.is_valid():
            usuario_form.save()
            docente_form.save()
            return redirect("listar_docentes")
    else:
        usuario_form = EditarUsuarioForm(instance=usuario)
        docente_form = DocenteForm(instance=docente)

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



def crear_tareas_docente(request):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # Cursos asignados al docente
    cursos = []

    if docente.curso:
        cursos = [docente.curso]

    if request.method == "POST":

        tarea_form = TareasForm(
            request.POST,
            request.FILES
        )

        curso_id = request.POST.get("curso")

        if not curso_id:

            messages.error(
                request,
                "Debes seleccionar un curso."
            )

        else:

            # Solo permitir cursos del docente
            if not docente.curso:

                messages.error(
                    request,
                    "No tienes ningún curso asignado."
                )

            elif str(curso_id) != str(docente.curso.id):

                messages.error(
                    request,
                    "No puedes asignar tareas a un curso que no tienes asignado."
                )

            elif tarea_form.is_valid():

                with transaction.atomic():

                    # Crear tarea
                    tarea = tarea_form.save(
                        commit=False
                    )

                    # Asignar curso
                    tarea.curso = docente.curso

                    # Asignar clase
                    if docente.clase:
                        tarea.clase = docente.clase

                    tarea.save()

                    # Imágenes
                    for imagen in request.FILES.getlist("imagenes"):
                        Imagen.objects.create(
                            tarea=tarea,
                            imagen=imagen
                        )

                    # Archivos
                    for archivo in request.FILES.getlist("archivos"):
                        ArchivoTarea.objects.create(
                            tarea=tarea,
                            archivo=archivo
                        )

                    # Videos
                    for video in request.POST.getlist("videos"):
                        video = video.strip()

                        if video:
                            Video.objects.create(
                                tarea=tarea,
                                video=video
                            )

                    # Preguntas
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
        }
    )

def editar_tarea_docente(request, tarea_id):

    # =====================================================
    # OBTENER DOCENTE
    # =====================================================

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # =====================================================
    # VERIFICAR QUE EL DOCENTE TENGA CURSO
    # =====================================================

    if not docente.curso:

        messages.error(
            request,
            "No tienes un curso asignado."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # =====================================================
    # OBTENER TAREA
    # =====================================================

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # =====================================================
    # VERIFICAR QUE LA TAREA PERTENEZCA AL CURSO
    # DEL DOCENTE
    # =====================================================

    if tarea.curso != docente.curso:

        messages.error(
            request,
            "No tienes permiso para editar esta tarea."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # =====================================================
    # CURSOS DISPONIBLES PARA EL TEMPLATE
    # SOLO EL CURSO DEL DOCENTE
    # =====================================================

    cursos = [
        docente.curso
    ]

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        tarea_form = TareasForm(
            request.POST,
            request.FILES,
            instance=tarea
        )

        # =================================================
        # CURSO SELECCIONADO
        # =================================================

        curso_id = request.POST.get("curso")

        if not curso_id:

            messages.error(
                request,
                "Debes seleccionar un curso."
            )

        else:

            # =============================================
            # OBTENER CURSO
            # =============================================

            curso = get_object_or_404(
                Cursos,
                id=curso_id
            )

            # =============================================
            # VERIFICAR QUE SEA EL CURSO DEL DOCENTE
            # =============================================

            if curso.id != docente.curso.id:

                messages.error(
                    request,
                    "No puedes asignar esta tarea a ese curso."
                )

            elif tarea_form.is_valid():

                try:

                    with transaction.atomic():

                        # =================================
                        # ACTUALIZAR TAREA
                        # =================================

                        tarea = tarea_form.save(
                            commit=False
                        )

                        # =================================
                        # FORZAR CURSO DEL DOCENTE
                        # =================================

                        tarea.curso = curso

                        # =================================
                        # FORZAR CLASE DEL DOCENTE
                        # =================================

                        if docente.clase:
                            tarea.clase = docente.clase

                        tarea.save()

                        # =================================
                        # IMÁGENES NUEVAS
                        # =================================

                        imagenes = request.FILES.getlist(
                            "imagenes"
                        )

                        for imagen in imagenes:

                            Imagen.objects.create(
                                tarea=tarea,
                                imagen=imagen
                            )

                        # =================================
                        # ARCHIVOS NUEVOS
                        # =================================

                        archivos = request.FILES.getlist(
                            "archivos"
                        )

                        for archivo in archivos:

                            ArchivoTarea.objects.create(
                                tarea=tarea,
                                archivo=archivo
                            )

                        # =================================
                        # VIDEOS NUEVOS
                        # =================================

                        videos = request.POST.getlist(
                            "videos"
                        )

                        for video_url in videos:

                            video_url = video_url.strip()

                            if video_url:

                                Video.objects.create(
                                    tarea=tarea,
                                    video=video_url
                                )

                        # =================================
                        # PREGUNTAS
                        # =================================

                        indices = []

                        for key in request.POST.keys():

                            if key.startswith("pregunta_"):

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

                        # =================================
                        # ELIMINAR ÍNDICES REPETIDOS
                        # =================================

                        indices = sorted(
                            set(indices)
                        )

                        # =================================
                        # PROCESAR PREGUNTAS
                        # =================================

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

                            # =================================
                            # VALIDAR ENUNCIADO
                            # =================================

                            if not enunciado:
                                continue

                            # =================================
                            # ACTUALIZAR PREGUNTA EXISTENTE
                            # =================================

                            if pregunta_id:

                                pregunta = get_object_or_404(
                                    Pregunta,
                                    id=pregunta_id,
                                    tarea=tarea
                                )

                                pregunta.descripcion = enunciado
                                pregunta.tipo = tipo

                                if puntaje:
                                    pregunta.puntaje = puntaje

                                pregunta.save()

                            # =================================
                            # CREAR PREGUNTA NUEVA
                            # =================================

                            else:

                                pregunta = Pregunta.objects.create(
                                    tarea=tarea,
                                    descripcion=enunciado,
                                    tipo=tipo,
                                    puntaje=(
                                        puntaje
                                        if puntaje
                                        else 1
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

                                # Marcar todas las opciones
                                # como incorrectas

                                OpcionesRespuesta.objects.filter(
                                    pregunta=pregunta
                                ).update(
                                    es_correcta=False
                                )

                            # =================================
                            # OPCIÓN MÚLTIPLE
                            # =================================

                            elif tipo == "opcion":

                                # ---------------------------------
                                # ELIMINAR RESPUESTA ABIERTA
                                # ---------------------------------

                                RespuestaCorrecta.objects.filter(
                                    pregunta=pregunta
                                ).delete()

                                # ---------------------------------
                                # OPCIONES RECIBIDAS
                                # ---------------------------------

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

                                # ---------------------------------
                                # OPCIONES EXISTENTES
                                # ---------------------------------

                                opciones_existentes = list(
                                    pregunta.opciones.all()
                                )

                                # ---------------------------------
                                # ACTUALIZAR / CREAR OPCIONES
                                # ---------------------------------

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

                                    # -----------------------------
                                    # ACTUALIZAR OPCIÓN EXISTENTE
                                    # -----------------------------

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

                                    # -----------------------------
                                    # CREAR OPCIÓN NUEVA
                                    # -----------------------------

                                    else:

                                        OpcionesRespuesta.objects.create(
                                            pregunta=pregunta,
                                            opcion=texto_opcion,
                                            es_correcta=es_correcta
                                        )

                    # =================================================
                    # ÉXITO
                    # =================================================

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

    # =====================================================
    # GET
    # =====================================================

    else:

        tarea_form = TareasForm(
            instance=tarea
        )

    # =====================================================
    # PREGUNTAS DE LA TAREA
    # =====================================================

    preguntas = (
        tarea.preguntas
        .prefetch_related(
            "opciones"
        )
        .all()
    )

    # =====================================================
    # CURSO ACTUAL
    # =====================================================

    curso_actual = tarea.curso

    # =====================================================
    # RENDER
    # =====================================================

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


def eliminar_tarea_docente(request, tarea_id):

    # Obtener docente
    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    # Obtener tarea
    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # Verificar que el docente tenga curso
    if not docente.curso:

        messages.error(
            request,
            "No tienes un curso asignado."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # Verificar que la tarea pertenezca
    # al curso del docente
    if tarea.curso != docente.curso:

        messages.error(
            request,
            "No tienes permiso para eliminar esta tarea."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # Eliminar tarea
    if request.method == "POST":

        tarea.delete()

        messages.success(
            request,
            "La tarea fue eliminada correctamente."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # Si entran directamente por GET,
    # mostrar confirmación
    return render(
        request,
        "paneles/docentes/tareas/eliminar_tarea.html",
        {
            "tarea": tarea,
        }
    )    


def listar_tareas(request):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    if docente.curso:

        tareas = Tareas.objects.filter(
            curso=docente.curso
        ).order_by("-fecha_creacion")

        # Total de estudiantes inscritos en el curso
        total_alumnos = Alumnos.objects.filter(
            curso=docente.curso
        ).count()

        # Calcular entregas de cada tarea
        for tarea in tareas:

            tarea.total_alumnos = total_alumnos

            tarea.entregas = (
                RespuestaAlumno.objects
                .filter(pregunta__tarea=tarea)
                .values("alumno")
                .distinct()
                .count()
            )

            if total_alumnos > 0:
                tarea.porcentaje_entrega = (
                    tarea.entregas / total_alumnos
                ) * 100
            else:
                tarea.porcentaje_entrega = 0

    else:

        tareas = Tareas.objects.none()
        total_alumnos = 0

    total_tareas = tareas.count()

    tareas_activas = tareas.filter(
        fecha_entrega__isnull=False
    ).count()

    tareas_sin_fecha = tareas.filter(
        fecha_entrega__isnull=True
    ).count()

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
    

def respuesta_alumnos(request, tarea_id):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # ==========================================
    # VERIFICAR PERMISO
    # ==========================================

    if docente.curso != tarea.curso:

        messages.error(
            request,
            "No tienes permiso para ver esta tarea."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # ==========================================
    # OBTENER ALUMNOS QUE RESPONDIERON
    # ==========================================

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

    alumnos = (
        Usuario.objects
        .filter(
            id__in=alumnos_ids
        )
    )

    # ==========================================
    # RENDERIZAR
    # ==========================================

    return render(
        request,
        "paneles/docentes/tareas/respuesta_alumnos.html",
        {
            "tarea": tarea,
            "alumnos": alumnos,
        }
    )


def ver_respuestas(request, tarea_id, alumno_id):

    docente = get_object_or_404(
        Docente,
        usuario=request.user
    )

    tarea = get_object_or_404(
        Tareas,
        id=tarea_id
    )

    # ==========================================
    # VERIFICAR PERMISO DEL DOCENTE
    # ==========================================

    if docente.curso != tarea.curso:

        messages.error(
            request,
            "No tienes permiso para ver esta tarea."
        )

        return redirect(
            "listar_tareas_docentes"
        )

    # ==========================================
    # OBTENER ALUMNO
    # ==========================================

    alumno = get_object_or_404(
        Usuario,
        id=alumno_id
    )

    # ==========================================
    # GUARDAR EVALUACIÓN
    # ==========================================

    if request.method == "POST":

        respuesta_id = request.POST.get(
            "respuesta_id"
        )

        nota = request.POST.get(
            "nota"
        )

        estado = request.POST.get(
            "estado"
        )

        # ======================================
        # OBTENER RESPUESTA
        # ======================================

        respuesta = get_object_or_404(
            RespuestaAlumno,
            id=respuesta_id,
            alumno_id=alumno_id,
            pregunta__tarea=tarea
        )

        # ======================================
        # CONVERTIR NOTA
        # ======================================

        try:

            nota = float(nota)

        except (TypeError, ValueError):

            nota = 0


        # ======================================
        # OBTENER PUNTAJE MÁXIMO
        # ======================================

        puntaje_maximo = float(
            respuesta.pregunta.puntaje
        )


        # ======================================
        # VALIDAR NOTA
        # ======================================

        if nota < 0:

            nota = 0


        if nota > puntaje_maximo:

            nota = puntaje_maximo


        # ======================================
        # GUARDAR NOTA
        # ======================================

        respuesta.nota_obtenida = nota


        # ======================================
        # GUARDAR ESTADO
        # ======================================

        if estado == "pending":

            respuesta.calificada = False

            respuesta.es_correcta = False

            respuesta.nota_obtenida = 0


        elif estado == "correct":

            respuesta.calificada = True

            respuesta.es_correcta = True

            respuesta.nota_obtenida = puntaje_maximo


        elif estado == "incorrect":

            respuesta.calificada = True

            respuesta.es_correcta = False

            respuesta.nota_obtenida = 0


        elif estado == "partial":

            respuesta.calificada = True

            respuesta.es_correcta = False

            # Conserva la nota que escribió el docente


        else:

            respuesta.calificada = True

            respuesta.es_correcta = (
                nota == puntaje_maximo
            )


        # ======================================
        # GUARDAR EN BASE DE DATOS
        # ======================================

        respuesta.save()


        # ======================================
        # MENSAJE
        # ======================================

        messages.success(
            request,
            "Evaluación guardada correctamente."
        )


        # ======================================
        # VOLVER AL LISTADO DE ALUMNOS
        # ======================================

        return redirect(
            "respuesta_alumnos",
            tarea_id=tarea.id
        )


    # ==========================================
    # OBTENER RESPUESTAS DEL ALUMNO
    # ==========================================

    respuestas = (
        RespuestaAlumno.objects
        .filter(
            alumno_id=alumno_id,
            pregunta__tarea=tarea
        )
        .select_related(
            "alumno",
            "pregunta",
            "opcion_seleccionada"
        )
        .prefetch_related(
            "pregunta__opciones"
        )
        .order_by(
            "pregunta__id"
        )
    )


    # ==========================================
    # OBTENER PREGUNTAS
    # ==========================================

    preguntas = (
        tarea.preguntas
        .all()
        .prefetch_related(
            "opciones"
        )
    )


    # ==========================================
    # CREAR DICCIONARIO DE RESPUESTAS
    # ==========================================

    respuestas_dict = {

        respuesta.pregunta_id: respuesta

        for respuesta in respuestas

    }


    # ==========================================
    # UNIR PREGUNTAS CON RESPUESTAS
    # ==========================================

    preguntas_respuestas = []


    for pregunta in preguntas:

        respuesta = respuestas_dict.get(
            pregunta.id
        )

        preguntas_respuestas.append({

            "pregunta": pregunta,

            "respuesta": respuesta,

        })


    # ==========================================
    # CALCULAR PUNTOS OBTENIDOS
    # ==========================================

    puntos_obtenidos = sum(

        respuesta.nota_obtenida

        for respuesta in respuestas

        if respuesta.calificada

    )


    # ==========================================
    # CALCULAR PUNTOS TOTALES
    # ==========================================

    puntos_totales = sum(

        pregunta.puntaje

        for pregunta in preguntas

    )


    # ==========================================
    # RENDERIZAR RESPUESTAS
    # ==========================================

    return render(

        request,

        "paneles/docentes/tareas/ver_respuesta.html",

        {

            "tarea": tarea,

            "alumno": alumno,

            "preguntas_respuestas":
                preguntas_respuestas,

            "puntos_obtenidos":
                puntos_obtenidos,

            "puntos_totales":
                puntos_totales,

            "total_preguntas":
                preguntas.count(),

            "respuestas":
                respuestas,

        }

    )