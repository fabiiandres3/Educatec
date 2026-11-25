import logging

from django.conf import settings
from django.core.mail import send_mass_mail
from django.db.models import Q
from django.urls import reverse

from apps.user.models import Notificacion, Usuario

logger = logging.getLogger(__name__)


def notificar_evento(request, evento):
    """Persist notices and email active users included in a published event audience."""
    roles_por_publico = {
        "todos": ("alumno", "docente", "acudiente"),
        "alumnos": ("alumno",),
        "docentes": ("docente",),
        "acudientes": ("acudiente",),
    }
    roles = roles_por_publico.get(evento.publico, ())
    if not evento.publicado or not roles:
        return 0, 0

    filtro_roles = Q()
    for role in roles:
        filtro_roles |= Q(rol__nombre__iexact=role)
    usuarios = list(
        Usuario.objects.filter(filtro_roles, is_active=True)
        .distinct()
    )

    url = request.build_absolute_uri(reverse("detalle_evento", args=[evento.pk]))
    momento = evento.fecha.strftime("%d/%m/%Y")
    mensaje = f"{evento.titulo} · {momento}. {evento.descripcion[:220]}"
    Notificacion.objects.bulk_create([
        Notificacion(
            usuario=usuario,
            titulo="Nuevo evento escolar",
            mensaje=mensaje,
            url=url,
            tipo="evento",
        )
        for usuario in usuarios
    ])

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return len(usuarios), 0

    asunto = f"Nuevo evento en Educatec: {evento.titulo}"
    cuerpo = (
        f"Se publicó un evento para tu comunidad educativa.\n\n"
        f"Evento: {evento.titulo}\nFecha: {momento}\n"
        f"Hora: {evento.hora_inicio or 'Por confirmar'}\n\n"
        f"{evento.descripcion}\n\nConsulta los detalles en: {url}"
    )
    remitente = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    correos = [
        (asunto, cuerpo, remitente, [usuario.email])
        for usuario in usuarios if usuario.email
    ]
    try:
        enviados = send_mass_mail(tuple(correos), fail_silently=False) if correos else 0
    except Exception:
        logger.exception("No se pudieron enviar correos del evento %s", evento.pk)
        enviados = 0
    return len(usuarios), enviados
