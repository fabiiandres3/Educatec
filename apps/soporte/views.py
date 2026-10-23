import imaplib
import logging
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parseaddr

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET

from apps.user import decorators
from apps.user.models import Usuario


@login_required
def solicitud_soporte(request):
    destino = request.POST.get("next", "") if request.method == "POST" else request.GET.get("next", "")
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
            administradores = Usuario.objects.filter(
                rol__nombre__iexact="administrador",
                is_active=True,
            ).exclude(email__isnull=True).exclude(email__exact="").values_list("email", flat=True)
            correos_administradores = {correo.strip() for correo in administradores if correo and correo.strip()}
            buzon_soporte = getattr(settings, "EMAIL_HOST_USER", "").strip()
            destinatarios = correos_administradores | ({buzon_soporte} if buzon_soporte else set())
            destinatarios.add(correo_solicitante)

            if not correos_administradores:
                errores.append("No hay administradores con un correo válido para recibir solicitudes.")
            else:
                nombre = request.user.get_full_name() or request.user.username
                rol = request.user.rol.nombre if request.user.rol else "Sin rol"
                asunto_correo = f"[Soporte Educatec] {asunto}"
                cuerpo = (
                    f"Solicitud de soporte recibida desde Educatec.\n\n"
                    f"Asunto: {asunto}\n"
                    f"Solicitante: {nombre}\n"
                    f"Correo: {correo_solicitante}\n"
                    f"Rol: {rol}\n"
                    f"Usuario: {request.user.username}\n\n"
                    f"Mensaje:\n{mensaje}\n"
                )
                correo_principal = buzon_soporte or sorted(correos_administradores, key=str.casefold)[0]
                correo = EmailMessage(
                    subject=asunto_correo,
                    body=cuerpo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[correo_principal],
                    bcc=sorted(destinatarios - {correo_principal}, key=str.casefold),
                    reply_to=[correo_solicitante],
                    headers={"X-Educatec-Support": "1"},
                )
                try:
                    correo.send(fail_silently=False)
                    messages.success(request, "Tu solicitud fue enviada a todos los administradores.")
                    if next_url:
                        return redirect(next_url)
                    from apps.user.views import obtener_panel_por_rol
                    return redirect(obtener_panel_por_rol(request.user.rol.nombre) if request.user.rol else "index")
                except Exception:
                    logging.getLogger(__name__).exception("No se pudo enviar una solicitud de soporte.")
                    errores.append("No se pudo enviar la solicitud. Inténtalo de nuevo más tarde.")

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
    configured_email = getattr(settings, "EMAIL_HOST_USER", "")
    cache_key = f"admin-support-inbox-v5-{request.user.pk}"
    cached_payload = cache.get(cache_key)
    if cached_payload is not None:
        return JsonResponse(cached_payload)

    if not configured_email or not getattr(settings, "EMAIL_HOST_PASSWORD", ""):
        payload = {"connected": False, "unread_count": 0, "emails": [], "gmail_url": ""}
        cache.set(cache_key, payload, 30)
        return JsonResponse(payload)

    mailbox = None
    try:
        mailbox = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=6)
        mailbox.login(configured_email, settings.EMAIL_HOST_PASSWORD)
        status, _ = mailbox.select("INBOX", readonly=True)
        if status != "OK":
            raise imaplib.IMAP4.error("No fue posible abrir la bandeja de entrada")

        status, search_data = mailbox.uid("search", None, "ALL")
        if status != "OK":
            raise imaplib.IMAP4.error("No fue posible consultar la bandeja de entrada")

        message_ids = search_data[0].split() if search_data and search_data[0] else []
        newest_first = list(reversed(message_ids[-500:]))
        support_subject_prefix = "[soporte educatec]"
        configured_sender = configured_email.strip().casefold()
        unread_support_count = 0
        emails = []

        for start_index in range(0, len(newest_first), 50):
            batch_ids = newest_first[start_index:start_index + 50]
            status, message_data = mailbox.uid(
                "fetch",
                b",".join(batch_ids),
                "(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])",
            )
            if status != "OK":
                continue

            for part in message_data:
                if not isinstance(part, tuple):
                    continue
                response_header = part[0]
                parsed_message = message_from_bytes(part[1])
                try:
                    subject = str(make_header(decode_header(parsed_message.get("Subject", ""))))
                    sender = str(make_header(decode_header(parsed_message.get("From", ""))))
                except (TypeError, ValueError, UnicodeError):
                    subject = parsed_message.get("Subject", "")
                    sender = parsed_message.get("From", "")

                sender_address = parseaddr(sender)[1].strip().casefold()
                if not subject.casefold().startswith(support_subject_prefix):
                    continue
                if sender_address != configured_sender:
                    continue

                is_unread = b"\\Seen" not in response_header
                unread_support_count += int(is_unread)
                if len(emails) < 10:
                    emails.append({
                        "subject": subject or "Sin asunto",
                        "sender": sender or "Remitente desconocido",
                        "date": parsed_message.get("Date", ""),
                        "unread": is_unread,
                    })

        from urllib.parse import quote
        gmail_search = f'in:inbox from:{configured_email} subject:"[Soporte Educatec]"'
        gmail_url = f"https://mail.google.com/mail/u/0/?authuser={quote(configured_email)}#search/{quote(gmail_search, safe='')}"
        payload = {
            "connected": True,
            "unread_count": unread_support_count,
            "emails": emails,
            "gmail_url": gmail_url,
        }
    except (imaplib.IMAP4.error, OSError, TimeoutError, ValueError):
        logging.getLogger(__name__).warning("No fue posible consultar el buzón de soporte de Gmail para el administrador.", exc_info=True)
        payload = {"connected": False, "unread_count": 0, "emails": [], "gmail_url": ""}
    finally:
        if mailbox is not None:
            try:
                mailbox.logout()
            except (imaplib.IMAP4.error, OSError):
                pass

    cache.set(cache_key, payload, 30)
    return JsonResponse(payload)
