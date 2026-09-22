from io import BytesIO

from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.alumnos.models import Alumnos
from apps.docentes.models import AsignacionDocente, Docente
from apps.horario.models import Periodo
from apps.user.decorators import rol_requerido

from .forms import ContenidoPedagogicoForm, ObservacionBoletinForm
from .models import ContenidoPedagogico, ObservacionBoletin
from .services import construir_boletin


def _periodos():
    return Periodo.objects.order_by("-anio", "numero")


def _asignaciones_curso(curso):
    return AsignacionDocente.objects.filter(curso=curso).select_related(
        "docente__usuario", "curso", "clase"
    ).order_by("clase__titulo", "docente__usuario__last_name")


@rol_requerido("docente")
def boletines_docente(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    asignaciones = AsignacionDocente.objects.filter(docente=docente).select_related("curso", "clase")
    asignacion = None
    periodo = None
    filas = []
    if request.GET.get("asignacion"):
        asignacion = get_object_or_404(asignaciones, pk=request.GET["asignacion"])
    if request.GET.get("periodo"):
        periodo = get_object_or_404(Periodo, pk=request.GET["periodo"])
    if asignacion and periodo:
        alumnos = Alumnos.objects.filter(curso=asignacion.curso, activo=True).select_related("usuario")
        for alumno in alumnos.order_by("usuario__last_name", "usuario__first_name"):
            boletin, _ = construir_boletin(alumno, periodo, asignaciones.filter(pk=asignacion.pk))
            filas.append({"alumno": alumno, **boletin[0]})
    return render(request, "boletin/docente_lista.html", {
        "asignaciones": asignaciones, "periodos": _periodos(), "asignacion": asignacion,
        "periodo": periodo, "filas": filas,
    })


@rol_requerido("docente")
def editar_boletin_docente(request, asignacion_id, alumno_id, periodo_id):
    docente = get_object_or_404(Docente, usuario=request.user)
    asignacion = get_object_or_404(AsignacionDocente, pk=asignacion_id, docente=docente)
    alumno = get_object_or_404(Alumnos.objects.select_related("usuario"), pk=alumno_id, curso=asignacion.curso, activo=True)
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    contenido, _ = ContenidoPedagogico.objects.get_or_create(asignacion=asignacion, periodo=periodo)
    observacion, _ = ObservacionBoletin.objects.get_or_create(contenido=contenido, alumno=alumno)
    if request.method == "POST":
        contenido_form = ContenidoPedagogicoForm(request.POST, instance=contenido)
        observacion_form = ObservacionBoletinForm(request.POST, instance=observacion)
        if contenido_form.is_valid() and observacion_form.is_valid():
            contenido_form.save()
            observacion_guardada = observacion_form.save(commit=False)
            observacion_guardada.publicado_en = (
                timezone.now() if observacion_guardada.publicado else None
            )
            observacion_guardada.save()
            messages.success(request, "La información del boletín fue guardada.")
            return redirect(f"{request.path}?guardado=1")
    else:
        contenido_form = ContenidoPedagogicoForm(instance=contenido)
        observacion_form = ObservacionBoletinForm(instance=observacion)
    filas, promedio = construir_boletin(alumno, periodo, AsignacionDocente.objects.filter(pk=asignacion.pk))
    return render(request, "boletin/docente_editar.html", {
        "alumno": alumno, "asignacion": asignacion, "periodo": periodo, "fila": filas[0],
        "promedio": promedio, "contenido_form": contenido_form, "observacion_form": observacion_form,
    })


@rol_requerido("alumno")
def mis_boletines(request):
    # Esta vista nunca recibe un alumno por URL: siempre usa exclusivamente el
    # perfil asociado al usuario autenticado.
    alumno = get_object_or_404(
        Alumnos.objects.select_related("usuario", "curso"),
        usuario_id=request.user.id,
        activo=True,
    )
    periodo = get_object_or_404(Periodo, pk=request.GET["periodo"]) if request.GET.get("periodo") else None
    # El alumno siempre debe poder consultar sus promedios académicos. La
    # publicación controla el estado de la observación, no la visibilidad de
    # las notas provenientes de Calificaciones.
    filas, promedio = (
        construir_boletin(
            alumno, periodo, _asignaciones_curso(alumno.curso),
            solo_con_notas=True,
        )
        if periodo and alumno.curso else ([], None)
    )
    return render(request, "boletin/alumno_boletin.html", {
        "alumno": alumno, "periodos": _periodos(), "periodo": periodo, "filas": filas, "promedio": promedio,
    })


@rol_requerido("administrador")
def boletines_administrador(request):
    from apps.cursos.models import Cursos
    curso_id, periodo_id = request.GET.get("curso"), request.GET.get("periodo")
    curso = get_object_or_404(Cursos, pk=curso_id) if curso_id else None
    periodo = get_object_or_404(Periodo, pk=periodo_id) if periodo_id else None
    filas = []
    if curso and periodo:
        asignaciones = _asignaciones_curso(curso)
        for alumno in Alumnos.objects.filter(curso=curso, activo=True).select_related("usuario").order_by("usuario__last_name"):
            boletin, promedio = construir_boletin(alumno, periodo, asignaciones)
            filas.append({"alumno": alumno, "promedio": promedio, "completo": bool(boletin) and all(f["completo"] for f in boletin), "pendientes": sum(not f["completo"] for f in boletin)})
    return render(request, "boletin/admin_lista.html", {"cursos": Cursos.objects.all(), "periodos": _periodos(), "curso": curso, "periodo": periodo, "filas": filas})


@rol_requerido("administrador")
def ver_boletin_administrador(request, alumno_id, periodo_id):
    alumno = get_object_or_404(Alumnos.objects.select_related("usuario", "curso"), pk=alumno_id)
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    filas, promedio = construir_boletin(
        alumno, periodo, _asignaciones_curso(alumno.curso),
    )
    return render(request, "boletin/boletin_detalle.html", {"alumno": alumno, "periodo": periodo, "filas": filas, "promedio": promedio, "es_administrador": True})


@rol_requerido("administrador", "alumno")
def descargar_boletin_pdf(request, alumno_id, periodo_id):
    alumno = get_object_or_404(Alumnos.objects.select_related("usuario", "curso"), pk=alumno_id)
    es_alumno = request.user.rol.nombre.lower().strip() == "alumno"
    if es_alumno and alumno.usuario_id != request.user.id:
        raise Http404
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    filas, promedio = construir_boletin(alumno, periodo, _asignaciones_curso(alumno.curso))
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
    from reportlab.lib import colors
    archivo = BytesIO()
    documento = SimpleDocTemplate(archivo, pagesize=letter, title="Boletín académico")
    estilos = getSampleStyleSheet()
    elementos = [Paragraph("EDUCATEC — Boletín académico", estilos["Title"]), Paragraph(f"Estudiante: {alumno.usuario.get_full_name() or alumno.usuario.username}<br/>Curso: {alumno.curso or 'No asignado'}<br/>Periodo: {periodo}", estilos["BodyText"]), Spacer(1, 12)]
    datos = [["Asignatura", "Docente", "Nota", "Desempeño"]] + [[str(f["materia"] or "Sin asignatura"), str(f["docente"]), str(f["nota"] or "—"), f["desempeno"]] for f in filas]
    tabla = Table(datos, colWidths=[150, 160, 60, 90])
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .25, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elementos += [tabla, Spacer(1, 12), Paragraph(f"Promedio general: {promedio if promedio is not None else 'Sin calificaciones'}", estilos["Heading3"])]
    for fila in filas:
        if fila["contenido"] or fila["observacion"]:
            texto = f"<b>{fila['materia'] or 'Asignatura'}</b><br/>"
            if fila["contenido"]:
                texto += f"Competencias: {fila['contenido'].competencias or '—'}<br/>Logros: {fila['contenido'].logros or '—'}<br/>"
            texto += f"Observación: {fila['observacion'].observacion if fila['observacion'] else 'Pendiente'}"
            elementos += [Spacer(1, 8), Paragraph(texto, estilos["BodyText"])]
    documento.build(elementos)
    archivo.seek(0)
    return FileResponse(archivo, as_attachment=True, filename=f"boletin_{alumno_id}_{periodo.anio}_{periodo.numero}.pdf")
