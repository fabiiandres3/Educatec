import imaplib
import logging
from datetime import timedelta
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parseaddr

from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from django.conf import settings

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMessage, send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


from django.urls import reverse

from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_encode, urlsafe_base64_decode

from django.utils.encoding import force_bytes, force_str

from apps.user.models import Usuario, Roles

from apps.user.forms import RegistrarForm, LoginForm, EditarUsuarioForm

from apps.user import decorators

from apps.user.tokens import email_verification_token

from apps.eventos.models import Evento
from apps.alumnos.models import Alumnos


@ensure_csrf_cookie
@require_GET
def refresh_csrf_token(request):
    response = JsonResponse({"csrfToken": get_token(request)})
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


# =========================================================
# PÁGINAS PÚBLICAS
# =========================================================


def index(request):

    # =========================================================
    # EVENTOS VISIBLES EN EL HOME
    # =========================================================

    if request.user.is_authenticated and request.user.rol:

        rol = request.user.rol.nombre.strip().lower()

        # ADMINISTRADOR
        if rol in ["administrador", "admin"]:
            eventos = Evento.objects.filter(
                publicado=True
            )

        # DOCENTE
        elif rol in ["docente", "docentes"]:
            eventos = Evento.objects.filter(
                publicado=True,
                publico__in=["todos", "docentes"]
            )

        # ALUMNO / ESTUDIANTE
        elif rol in ["alumno", "alumnos", "estudiante", "estudiantes"]:
            eventos = Evento.objects.filter(
                publicado=True,
                publico__in=["todos", "alumnos"]
            )

        # CUALQUIER OTRO ROL
        else:
            eventos = Evento.objects.filter(
                publicado=True,
                publico="todos"
            )

    else:
        # USUARIO NO AUTENTICADO
        # Solo puede ver eventos públicos para todos
        eventos = Evento.objects.filter(
            publicado=True,
            publico="todos"
        )

    # =========================================================
    # ORDENAR EVENTOS
    # =========================================================

    eventos = eventos.order_by(
        "fecha",
        "hora_inicio"
    )

    return render(
        request,
        "index.html",
        {
            "eventos": eventos,
        }
    )


def prescolar(request):

    return render(request, "programas/prescolar.html")


def primaria(request):

    return render(request, "programas/primaria.html")


def secundaria(request):

    return render(request, "programas/secundaria.html")


# =========================================================
# REDIRECCIÓN AUTOMÁTICA SEGÚN ROL
# =========================================================


def redireccionar_por_rol(request):

    # -----------------------------------------------------
    # USUARIO NO AUTENTICADO
    # -----------------------------------------------------

    if not request.user.is_authenticated:

        return redirect("login")

    # -----------------------------------------------------
    # USUARIO SIN ROL
    # -----------------------------------------------------

    if not request.user.rol:

        logout(request)

        return redirect("login")

    # -----------------------------------------------------
    # OBTENER ROL
    # -----------------------------------------------------

    rol = (
        request.user.rol.nombre
        .lower()
        .strip()
    )

    # -----------------------------------------------------
    # ADMINISTRADOR
    # -----------------------------------------------------

    if rol == "administrador":

        return redirect(
            "dashboard_administrador"
        )

    # -----------------------------------------------------
    # DOCENTE
    # -----------------------------------------------------

    elif rol == "docente":

        return redirect(
            "dashboard_docente"
        )

    # -----------------------------------------------------
    # ALUMNO
    # -----------------------------------------------------

    elif rol == "alumno":

        return redirect(
            "dashboard_alumnos"
        )

    # -----------------------------------------------------
    # ACUDIENTE
    # -----------------------------------------------------

    elif rol == "acudiente":

        return redirect(
            "dashboard_acudiente"
        )

    # -----------------------------------------------------
    # USUARIO
    # -----------------------------------------------------

    elif rol == "usuario":

        return redirect(
            "verificacion"
        )

    # -----------------------------------------------------
    # ROL DESCONOCIDO
    # -----------------------------------------------------

    logout(request)

    return redirect("login")

# =========================================================
# REGISTRO DE USUARIO
# =========================================================


def Registrar_usuario(request):

    # -----------------------------------------------------
    # Si ya está autenticado
    # -----------------------------------------------------

    if request.user.is_authenticated:
        return redirect("redireccionar_por_rol")

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":
        form = RegistrarForm(request.POST)

        if form.is_valid():
            # -------------------------------------------------
            # Obtener datos del formulario
            # -------------------------------------------------

            username = form.cleaned_data["username"]

            email = form.cleaned_data["email"]

            password = form.cleaned_data["password"]

            # -------------------------------------------------
            # Buscar rol "usuario"
            # -------------------------------------------------

            rol_usuario, _ = Roles.objects.get_or_create(
                nombre__iexact="usuario",
                defaults={"nombre": "Usuario"},
            )

            # -------------------------------------------------
            # Crear usuario
            # -------------------------------------------------

            usuario = form.save(commit=False)

            usuario.username = username

            usuario.email = email

            usuario.rol = rol_usuario

            # -------------------------------------------------
            # Guardar contraseña encriptada
            # -------------------------------------------------

            usuario.set_password(password)

            # -------------------------------------------------
            # La cuenta queda desactivada
            # hasta verificar el correo
            # -------------------------------------------------

            usuario.is_active = False

            # -------------------------------------------------
            # Guardar usuario
            # -------------------------------------------------

            usuario.save()

            # -------------------------------------------------
            # Generar token de verificación
            # -------------------------------------------------

            token = email_verification_token.make_token(usuario)

            # -------------------------------------------------
            # Codificar ID del usuario
            # -------------------------------------------------

            uid = urlsafe_base64_encode(force_bytes(usuario.pk))

            # -------------------------------------------------
            # Crear enlace de verificación
            # -------------------------------------------------

            verification_url = request.build_absolute_uri(
                reverse("verificar_correo", kwargs={"uidb64": uid, "token": token})
            )

            # -------------------------------------------------
            # Enviar correo de verificación
            # -------------------------------------------------

            try:
                send_mail(
                    subject=("Verifica tu cuenta de Educatec"),
                    message=(
                        f"Hola "
                        f"{usuario.first_name or usuario.username},\n\n"
                        "Gracias por registrarte "
                        "en Educatec.\n\n"
                        "Tu cuenta ha sido creada correctamente, "
                        "pero debes verificar tu correo electrónico "
                        "antes de poder iniciar sesión.\n\n"
                        "Haz clic en el siguiente enlace "
                        "para verificar tu correo:\n\n"
                        f"{verification_url}\n\n"
                        "Después de verificar tu correo "
                        "podrás iniciar sesión normalmente.\n\n"
                        "Si tú no creaste esta cuenta, "
                        "puedes ignorar este mensaje."
                    ),
                    from_email=(settings.DEFAULT_FROM_EMAIL),
                    recipient_list=[usuario.email],
                    fail_silently=False,
                )

            except Exception:
                # -------------------------------------------------
                # Si el correo no pudo enviarse,
                # eliminar la cuenta creada
                # -------------------------------------------------

                usuario.delete()

                messages.error(
                    request,
                    "No se pudo enviar el correo "
                    "de verificación. "
                    "La cuenta no fue creada. "
                    "Inténtalo nuevamente.",
                )

                return render(request, "login/registrar_usuario.html", {"form": form})

            # -------------------------------------------------
            # Mostrar mensaje de éxito
            # -------------------------------------------------

            messages.success(
                request,
                "Cuenta creada correctamente. "
                "Hemos enviado un enlace de verificación "
                "a tu correo electrónico. "
                "Revisa tu bandeja de entrada o spam.",
            )

            # -------------------------------------------------
            # Ir al login
            # -------------------------------------------------

            return redirect("login")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:
        form = RegistrarForm()

    # -----------------------------------------------------
    # Mostrar formulario
    # -----------------------------------------------------

    return render(request, "login/registrar_usuario.html", {"form": form})


# =========================================================
# VERIFICAR CORREO ELECTRÓNICO
# =========================================================


def verificar_correo(request, uidb64, token):

    # -----------------------------------------------------
    # Inicializar usuario
    # -----------------------------------------------------

    usuario = None

    # -----------------------------------------------------
    # Obtener usuario mediante UID
    # -----------------------------------------------------

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        usuario = Usuario.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    # -----------------------------------------------------
    # Verificar usuario y token
    # -----------------------------------------------------

    if usuario is not None and email_verification_token.check_token(usuario, token):
        # -------------------------------------------------
        # Activar cuenta
        # -------------------------------------------------

        usuario.is_active = True

        usuario.save(update_fields=["is_active"])

        # -------------------------------------------------
        # Mensaje de éxito
        # -------------------------------------------------

        messages.success(
            request,
            "Tu correo electrónico ha sido "
            "verificado correctamente. "
            "Ya puedes iniciar sesión.",
        )

        return redirect("login")

    # -----------------------------------------------------
    # Enlace inválido o expirado
    # -----------------------------------------------------

    messages.error(request, "El enlace de verificación no es válido o ha expirado.")

    return redirect("login")


# =========================================================
# LOGIN
# =========================================================


def iniciar_sesion(request):

    # -----------------------------------------------------
    # Si ya está autenticado
    # -----------------------------------------------------

    if request.user.is_authenticated:
        return redirect("redireccionar_por_rol")

    # -----------------------------------------------------
    # Crear formulario
    # -----------------------------------------------------

    form = LoginForm(request.POST or None)

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":
        if form.is_valid():
            identificador = form.cleaned_data["username"]

            password = form.cleaned_data["password"]

            # -------------------------------------------------
            # Buscar usuario
            # -------------------------------------------------

            try:
                usuario_existente = Usuario.objects.get(documento__iexact=identificador)

            except Usuario.DoesNotExist:
                try:
                    usuario_existente = Usuario.objects.get(username__iexact=identificador)
                except Usuario.DoesNotExist:
                    usuario_existente = None

            # -------------------------------------------------
            # Verificar si la cuenta existe pero
            # todavía no ha confirmado su correo
            # -------------------------------------------------

            if usuario_existente and not usuario_existente.is_active:
                messages.error(
                    request,
                    "Tu cuenta todavía no está activada. "
                    "Debes verificar el correo electrónico "
                    "que recibiste al registrarte.",
                )

                return render(request, "login/login.html", {"form": form})

            # -------------------------------------------------
            # Autenticar usuario
            # -------------------------------------------------

            usuario = authenticate(
                request=request,
                username=(usuario_existente.username if usuario_existente else identificador),
                password=password,
            )

            # -------------------------------------------------
            # Login correcto
            # -------------------------------------------------

            if usuario is not None:
                login(request, usuario)

                messages.success(request, f"Bienvenido, {usuario.username}.")

                return redirect("redireccionar_por_rol")

            # -------------------------------------------------
            # Login incorrecto
            # -------------------------------------------------

            messages.error(request, "Usuario o contraseña incorrectos.")

    # -----------------------------------------------------
    # Mostrar login
    # -----------------------------------------------------

    return render(request, "login/login.html", {"form": form})


# =========================================================
# CERRAR SESIÓN
# =========================================================


def cerrar_sesion(request):

    if request.user.is_authenticated:
        logout(request)

    return redirect("index")


# =========================================================
# USUARIO NORMAL
# =========================================================


#@decorators.rol_requerido("usuario")
def verificacion(request):

    return render(request, "login/verificacion.html")


# =========================================================
# ADMINISTRADOR
# =========================================================


#@decorators.rol_requerido("administrador")
@decorators.rol_requerido("administrador")
def dashboard(request):
    if request.method == "POST" and request.POST.get("accion") == "asignar_rol":
        usuario = get_object_or_404(
            Usuario,
            pk=request.POST.get("usuario_id"),
            rol__nombre__iexact="usuario",
        )
        rol = get_object_or_404(Roles, pk=request.POST.get("rol_id"))
        usuario.rol = rol
        usuario.save(update_fields=["rol"])
        messages.success(
            request,
            f"Se asignó el rol {rol.nombre} a {usuario.get_full_name() or usuario.username}.",
        )
        return redirect("dashboard_administrador")

    limite_recientes = timezone.now() - timedelta(days=15)
    usuarios = Usuario.objects.all()
    pendientes = usuarios.filter(
        rol__nombre__iexact="usuario",
        date_joined__gte=limite_recientes,
    )
    usuarios_recientes = usuarios.filter(
        date_joined__gte=limite_recientes,
    ).select_related("rol").order_by("-date_joined")[:10]
    usuarios_pendientes_rol = pendientes.select_related("rol").order_by("-date_joined")[:10]

    return render(
        request,
        "admin/dashboard.html",
        {
            "usuarios_recientes": usuarios_recientes,
            "usuarios_pendientes_rol": usuarios_pendientes_rol,
            "total_pendientes_rol": pendientes.count(),
            "total_usuarios": usuarios.count(),
            "total_usuarios_activos": usuarios.filter(is_active=True).count(),
            "total_usuarios_semana": usuarios.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            ).count(),
            "roles_disponibles": Roles.objects.order_by("nombre"),
        },
    )
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
                correo = EmailMessage(
                    subject=asunto_correo,
                    body=cuerpo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[buzon_soporte] if buzon_soporte else [sorted(correos_administradores, key=str.casefold)[0]],
                    bcc=sorted(destinatarios - {buzon_soporte} if buzon_soporte else destinatarios - {sorted(correos_administradores, key=str.casefold)[0]}, key=str.casefold),
                    reply_to=[correo_solicitante],
                    headers={"X-Educatec-Support": "1"},
                )
                try:
                    correo.send(fail_silently=False)
                    messages.success(request, "Tu solicitud fue enviada a todos los administradores.")
                    if next_url:
                        return redirect(next_url)
                    return redirect(obtener_panel_por_rol(request.user.rol.nombre) if request.user.rol else "index")
                except Exception:
                    logging.getLogger(__name__).exception("No se pudo enviar una solicitud de soporte.")
                    errores.append("No se pudo enviar la solicitud. Inténtalo de nuevo más tarde.")

    return render(request, "paneles/solicitud_soporte.html", {
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

        # Revisa los correos más recientes con IMAP estándar y solo conserva soporte.
        status, search_data = mailbox.uid("search", None, "ALL")
        if status != "OK":
            raise imaplib.IMAP4.error("No fue posible consultar la bandeja de entrada")

        message_ids = search_data[0].split() if search_data and search_data[0] else []
        newest_first = list(reversed(message_ids[-500:]))
        support_subject_prefix = "[soporte educatec]"
        configured_sender = configured_email.strip().casefold()
        unread_support_count = 0
        emails = []

        # BODY.PEEK mantiene el estado de lectura original de cada correo.
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
# =========================================================
# LISTAR USUARIOS
# =========================================================


@decorators.rol_requerido("administrador")
def Listar_usuarios(request):

    usuarios = Usuario.objects.filter(rol__nombre__iexact="usuario").select_related("rol")

    return render(request, "admin/usuarios/usuarios.html", {
        "usuarios": usuarios,
        "usuarios_activos": usuarios.filter(is_active=True).count(),
        "usuarios_inactivos": usuarios.filter(is_active=False).count(),
    })


# =========================================================
# EDITAR USUARIO
# =========================================================


@decorators.rol_requerido("administrador")
def Editar_usuario(request, usuario_id):

    usuario = get_object_or_404(Usuario, id=usuario_id)
    fecha_nacimiento_registrada = usuario.fecha_nacimiento
    if not fecha_nacimiento_registrada:
        fecha_nacimiento_registrada = Alumnos.objects.filter(
            usuario=usuario
        ).values_list("fecha_nacimiento", flat=True).first()
    datos_iniciales = {"fecha_nacimiento": fecha_nacimiento_registrada}

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":
        usuario_form = EditarUsuarioForm(
            request.POST,
            instance=usuario,
            initial=datos_iniciales,
        )

        if usuario_form.is_valid():
            usuario_form.save()
            messages.success(request, "Usuario editado correctamente.")

            return redirect("listar_usuarios")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:
        usuario_form = EditarUsuarioForm(
            instance=usuario,
            initial=datos_iniciales,
        )

    return render(
        request, "admin/usuarios/editar_usuario.html", {"usuario_form": usuario_form}
    )


# =========================================================
# ELIMINAR USUARIO
# =========================================================


@decorators.rol_requerido("administrador")
def Eliminar_usuario(request, usuario_id):

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":
        nombre_usuario = usuario.get_full_name() or usuario.documento
        usuario.delete()
        messages.success(request, f"Usuario {nombre_usuario} eliminado correctamente.")

        return redirect("listar_usuarios")

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(request, "admin/usuarios/eliminar_usuario.html", {"usuario": usuario})
