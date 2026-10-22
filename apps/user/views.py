from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout

from django.core.mail import send_mail

from django.conf import settings

from django.urls import reverse

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.utils.encoding import force_bytes, force_str

from apps.user.models import Usuario, Roles

from apps.user.forms import RegistrarForm, LoginForm, EditarUsuarioForm

from apps.user import decorators

from apps.user.tokens import email_verification_token

from apps.eventos.models import Evento
from apps.alumnos.models import Alumnos
from apps.docentes.models import Docente
from apps.tareas.models import Tareas
from apps.cursos.models import Cursos
from apps.clases.models import Clases


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

    meses = ("ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC")
    eventos_home = []
    for evento in eventos:
        hora = ""
        if evento.hora_inicio:
            hora = evento.hora_inicio.strftime("%H:%M")
            if evento.hora_fin:
                hora += f" – {evento.hora_fin.strftime('%H:%M')}"
        eventos_home.append({
            "id": evento.id,
            "tipo": evento.tipo,
            "titulo": evento.titulo,
            "descripcion": evento.descripcion,
            "dia": evento.fecha.strftime("%d"),
            "mes": meses[evento.fecha.month - 1],
            "hora": hora,
            "img": evento.imagen.url if evento.imagen else "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=900",
            "url": reverse("detalle_evento", kwargs={"id": evento.id}),
        })
    return render(
        request,
        "index.html",
        {
            "eventos": eventos,
            "eventos_home": eventos_home,
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

            try:
                rol_usuario = Roles.objects.get(nombre__iexact="usuario")

            except Roles.DoesNotExist:
                form.add_error(
                    None,
                    "No existe el rol 'usuario'. "
                    "Debes crear el rol usuario antes "
                    "de registrar una cuenta.",
                )

                return render(request, "login/registrar_usuario.html", {"form": form})

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


    usuarios_recientes = Usuario.objects.select_related("rol").order_by(
        "-date_joined"
    )[:10]

    # --------------------------------------------------------
    # MÉTRICAS REALES DEL PANEL
    # --------------------------------------------------------

    total_alumnoss = Alumnos.objects.filter(activo=True).count()
    total_docentees = Docente.objects.count()
    total_tareas = Tareas.objects.count()
    total_cursos = Cursos.objects.count()
    total_materias = Clases.objects.count()

    return render(
        request,
        "admin/dashboard.html",
        {
            "usuarios_recientes": usuarios_recientes,
            "total_alumnoss": total_alumnoss,
            "total_docentees": total_docentees,
            "total_tareas": total_tareas,
            "total_cursos": total_cursos,
            "total_materias": total_materias,
        }
    )


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
