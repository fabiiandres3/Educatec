import logging
import smtplib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET

from apps.user import decorators
from apps.user.models import Usuario
from apps.soporte.models import SolicitudSoporte


@login_required
def solicitud_soporte(request):
    if request.method == "POST":
        destino = request.POST.get("next", "")
    else:
        destino = request.GET.get("next", "") or request.META.get("HTTP_REFERER", "")
    next_url = destino if url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ) else ""
    asunto = ""
    mensaje = ""
    errores = []

    if request.method == "POST":
        asunto = request.POST.get("asunto", "").strip().replace("\r", " ").replace("\n", " ")
        mensaje = request.POST.get("mensaje", "").strip()
        correo_solicitante = (request.user.email or "").strip()
        if not correo_solicitante:
            errores.append("Completa un correo electrónico en tu perfil antes de solicitar soporte.")
        else:
            try:
                validate_email(correo_solicitante)
            except ValidationError:
                errores.append("El correo de tu perfil no tiene un formato válido. Actualízalo antes de solicitar soporte.")
        if len(asunto) < 4 or len(asunto) > 120:
            errores.append("El asunto debe tener entre 4 y 120 caracteres.")
        if len(mensaje) < 10 or len(mensaje) > 5000:
            errores.append("Describe la solicitud con entre 10 y 5000 caracteres.")

        if not errores:
            rol = request.user.rol.nombre if request.user.rol else "Sin rol"
            nombre = request.user.get_full_name() or request.user.username
            solicitud = SolicitudSoporte.objects.create(
                solicitante=request.user,
                nombre_solicitante=nombre,
                correo_solicitante=correo_solicitante,
                rol_solicitante=rol,
                asunto=asunto,
                mensaje=mensaje,
            )
            administradores = Usuario.objects.filter(
                rol__nombre__iexact="administrador",
                is_active=True,
            ).exclude(email__isnull=True).exclude(email__exact="").values_list("email", flat=True)
            correos_administradores = {correo.strip() for correo in administradores if correo and correo.strip()}
            buzon_soporte = (getattr(settings, "EMAIL_HOST_USER", "") or "").strip()
            contrasena_correo = getattr(settings, "EMAIL_HOST_PASSWORD", "")
            destinatarios = correos_administradores | ({buzon_soporte} if buzon_soporte else set())
            destinatarios.add(correo_solicitante)

            messages.success(request, "Reporte enviado correctamente.")
            if buzon_soporte and contrasena_correo:
                asunto_correo = f"[Soporte Educatec] {asunto}"
                cuerpo = (
                    f"Solicitud de soporte recibida desde Educatec.\n\n"
                    f"Asunto: {asunto}\n"
                    f"Solicitante: {nombre}\n"
                    f"Correo: {correo_solicitante}\n"
                    f"Rol: {rol}\n"
                    f"Usuario: {request.user.username}\n\n"
                    f"Mensaje:\n{mensaje}\n\n"
                    f"Solicitud interna: #{solicitud.pk}\n"
                )
                correo_principal = buzon_soporte
                correo = EmailMessage(
                    subject=asunto_correo,
                    body=cuerpo,
                    from_email=settings.DEFAULT_FROM_EMAIL or buzon_soporte,
                    to=[correo_principal],
                    bcc=sorted(destinatarios - {correo_principal}, key=str.casefold),
                    reply_to=[correo_solicitante],
                    headers={"X-Educatec-Support": "1"},
                )
                try:
                    if correo.send(fail_silently=False) != 1:
                        raise smtplib.SMTPException("El servidor de correo no aceptó la solicitud.")
                except (smtplib.SMTPException, OSError, ValueError):
                    logging.getLogger(__name__).exception("No se pudo enviar una solicitud de soporte.")
                    messages.warning(
                        request,
                        "El reporte quedó guardado, pero no se pudo enviar la notificación por correo.",
                    )

            if next_url:
                return redirect(next_url)
            from apps.user.views import obtener_panel_por_rol
            return redirect(obtener_panel_por_rol(request.user.rol.nombre) if request.user.rol else "index")

    return render(request, "soporte/solicitud_soporte.html", {
        "next_url": next_url,
        "asunto": asunto,
        "mensaje": mensaje,
        "correo_solicitante": (request.user.email or "").strip(),
        "errores": errores,
    })


@require_GET
@decorators.rol_requerido("administrador")
def notificaciones_correo_admin(request):
    solicitudes = SolicitudSoporte.objects.all()
    emails = [
        {
            "subject": solicitud.asunto,
            "sender": f"{solicitud.nombre_solicitante} <{solicitud.correo_solicitante}>",
            "date": solicitud.creada.isoformat(),
            "message": solicitud.mensaje,
            "role": solicitud.rol_solicitante,
            "unread": False,
        }
        for solicitud in solicitudes[:20]
    ]
    return JsonResponse({
        "connected": True,
        "unread_count": solicitudes.count(),
        "emails": emails,
        "gmail_url": "",
    })
