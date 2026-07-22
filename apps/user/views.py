from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.core.mail import send_mail

from django.conf import settings

from django.urls import reverse

from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)

from django.utils.encoding import (
    force_bytes,
    force_str
)

from apps.user.models import (
    Usuario,
    Roles
)

from apps.user.forms import (
    RegistrarForm,
    LoginForm,
    EditarUsuarioForm
)

from apps.user import decorators

from apps.user.tokens import (
    email_verification_token
)


# =========================================================
# PÁGINAS PÚBLICAS
# =========================================================


def index(request):

    return render(
        request,
        "index.html"
    )


def prescolar(request):

    return render(
        request,
        "programas/prescolar.html"
    )


def primaria(request):

    return render(
        request,
        "programas/primaria.html"
    )


def secundaria(request):

    return render(
        request,
        "programas/secundaria.html"
    )


# =========================================================
# REDIRECCIÓN AUTOMÁTICA SEGÚN ROL
# =========================================================


def redireccionar_por_rol(request):

    # -----------------------------------------------------
    # Usuario no autenticado
    # -----------------------------------------------------

    if not request.user.is_authenticated:

        return redirect(
            "login"
        )


    # -----------------------------------------------------
    # Usuario sin rol
    # -----------------------------------------------------

    if not request.user.rol:

        logout(request)

        return redirect(
            "login"
        )


    # -----------------------------------------------------
    # Obtener rol
    # -----------------------------------------------------

    rol = (
        request.user.rol.nombre
        .lower()
        .strip()
    )


    # -----------------------------------------------------
    # Administrador
    # -----------------------------------------------------

    if rol == "administrador":

        return redirect(
            "dashboard_administrador"
        )


    # -----------------------------------------------------
    # Docente
    # -----------------------------------------------------

    elif rol == "docente":

        return redirect(
            "dashboard_docente"
        )


    # -----------------------------------------------------
    # Alumno
    # -----------------------------------------------------

    elif rol == "alumno":

        return redirect(
            "dashboard_alumno"
        )


    # -----------------------------------------------------
    # Usuario normal
    # -----------------------------------------------------

    elif rol == "usuario":

        return redirect(
            "verificacion"
        )


    # -----------------------------------------------------
    # Rol desconocido
    # -----------------------------------------------------

    logout(request)

    return redirect(
        "login"
    )


# =========================================================
# REGISTRO DE USUARIO
# =========================================================


def Registrar_usuario(request):

    # -----------------------------------------------------
    # Si ya está autenticado
    # -----------------------------------------------------

    if request.user.is_authenticated:

        return redirect(
            "redireccionar_por_rol"
        )


    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        form = RegistrarForm(
            request.POST
        )


        if form.is_valid():

            # -------------------------------------------------
            # Obtener datos del formulario
            # -------------------------------------------------

            username = (
                form.cleaned_data["username"]
            )

            email = (
                form.cleaned_data["email"]
            )

            password = (
                form.cleaned_data["password"]
            )


            # -------------------------------------------------
            # Buscar rol "usuario"
            # -------------------------------------------------

            try:

                rol_usuario = Roles.objects.get(
                    nombre__iexact="usuario"
                )


            except Roles.DoesNotExist:

                form.add_error(
                    None,
                    "No existe el rol 'usuario'. "
                    "Debes crear el rol usuario antes "
                    "de registrar una cuenta."
                )

                return render(

                    request,

                    "login/registrar_usuario.html",

                    {
                        "form": form
                    }

                )


            # -------------------------------------------------
            # Crear usuario
            # -------------------------------------------------

            usuario = form.save(
                commit=False
            )


            usuario.username = username

            usuario.email = email

            usuario.rol = rol_usuario


            # -------------------------------------------------
            # Guardar contraseña encriptada
            # -------------------------------------------------

            usuario.set_password(
                password
            )


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

            token = (
                email_verification_token.make_token(
                    usuario
                )
            )


            # -------------------------------------------------
            # Codificar ID del usuario
            # -------------------------------------------------

            uid = (
                urlsafe_base64_encode(
                    force_bytes(
                        usuario.pk
                    )
                )
            )


            # -------------------------------------------------
            # Crear enlace de verificación
            # -------------------------------------------------

            verification_url = (

                request.build_absolute_uri(

                    reverse(

                        "verificar_correo",

                        kwargs={

                            "uidb64": uid,

                            "token": token

                        }

                    )

                )

            )


            # -------------------------------------------------
            # Enviar correo de verificación
            # -------------------------------------------------

            try:

                send_mail(

                    subject=(
                        "Verifica tu cuenta de Educatec"
                    ),

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

                    from_email=(
                        settings.DEFAULT_FROM_EMAIL
                    ),

                    recipient_list=[

                        usuario.email

                    ],

                    fail_silently=False

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
                    "Inténtalo nuevamente."

                )


                return render(

                    request,

                    "login/registrar_usuario.html",

                    {
                        "form": form
                    }

                )


            # -------------------------------------------------
            # Mostrar mensaje de éxito
            # -------------------------------------------------

            messages.success(

                request,

                "Cuenta creada correctamente. "
                "Hemos enviado un enlace de verificación "
                "a tu correo electrónico. "
                "Revisa tu bandeja de entrada o spam."

            )


            # -------------------------------------------------
            # Ir al login
            # -------------------------------------------------

            return redirect(
                "login"
            )


    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:

        form = RegistrarForm()


    # -----------------------------------------------------
    # Mostrar formulario
    # -----------------------------------------------------

    return render(

        request,

        "login/registrar_usuario.html",

        {
            "form": form
        }

    )


# =========================================================
# VERIFICAR CORREO ELECTRÓNICO
# =========================================================


def verificar_correo(
    request,
    uidb64,
    token
):

    # -----------------------------------------------------
    # Inicializar usuario
    # -----------------------------------------------------

    usuario = None


    # -----------------------------------------------------
    # Obtener usuario mediante UID
    # -----------------------------------------------------

    try:

        uid = force_str(

            urlsafe_base64_decode(

                uidb64

            )

        )


        usuario = Usuario.objects.get(

            pk=uid

        )


    except (

        TypeError,

        ValueError,

        OverflowError,

        Usuario.DoesNotExist

    ):

        usuario = None


    # -----------------------------------------------------
    # Verificar usuario y token
    # -----------------------------------------------------

    if (

        usuario is not None

        and

        email_verification_token.check_token(

            usuario,

            token

        )

    ):

        # -------------------------------------------------
        # Activar cuenta
        # -------------------------------------------------

        usuario.is_active = True


        usuario.save(

            update_fields=[

                "is_active"

            ]

        )


        # -------------------------------------------------
        # Mensaje de éxito
        # -------------------------------------------------

        messages.success(

            request,

            "Tu correo electrónico ha sido "
            "verificado correctamente. "
            "Ya puedes iniciar sesión."

        )


        return redirect(

            "login"

        )


    # -----------------------------------------------------
    # Enlace inválido o expirado
    # -----------------------------------------------------

    messages.error(

        request,

        "El enlace de verificación no es válido "
        "o ha expirado."

    )


    return redirect(

        "login"

    )


# =========================================================
# LOGIN
# =========================================================


def iniciar_sesion(request):

    # -----------------------------------------------------
    # Si ya está autenticado
    # -----------------------------------------------------

    if request.user.is_authenticated:

        return redirect(

            "redireccionar_por_rol"

        )


    # -----------------------------------------------------
    # Crear formulario
    # -----------------------------------------------------

    form = LoginForm(

        request.POST or None

    )


    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        if form.is_valid():

            username = (

                form.cleaned_data["username"]

            )


            password = (

                form.cleaned_data["password"]

            )


            # -------------------------------------------------
            # Buscar usuario
            # -------------------------------------------------

            try:

                usuario_existente = Usuario.objects.get(

                    username__iexact=username

                )


            except Usuario.DoesNotExist:

                usuario_existente = None


            # -------------------------------------------------
            # Verificar si la cuenta existe pero
            # todavía no ha confirmado su correo
            # -------------------------------------------------

            if (

                usuario_existente

                and

                not usuario_existente.is_active

            ):

                messages.error(

                    request,

                    "Tu cuenta todavía no está activada. "
                    "Debes verificar el correo electrónico "
                    "que recibiste al registrarte."

                )

                return render(

                    request,

                    "login/login.html",

                    {
                        "form": form
                    }

                )


            # -------------------------------------------------
            # Autenticar usuario
            # -------------------------------------------------

            usuario = authenticate(

                request=request,

                username=username,

                password=password

            )


            # -------------------------------------------------
            # Login correcto
            # -------------------------------------------------

            if usuario is not None:

                login(

                    request,

                    usuario

                )


                messages.success(

                    request,

                    f"Bienvenido, "
                    f"{usuario.username}."

                )


                return redirect(

                    "redireccionar_por_rol"

                )


            # -------------------------------------------------
            # Login incorrecto
            # -------------------------------------------------

            messages.error(

                request,

                "Usuario o contraseña incorrectos."

            )


    # -----------------------------------------------------
    # Mostrar login
    # -----------------------------------------------------

    return render(

        request,

        "login/login.html",

        {

            "form": form

        }

    )


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


@decorators.rol_requerido(

    "usuario"

)
def verificacion(request):

    return render(

        request,

        "login/verificacion.html"

    )


# =========================================================
# ADMINISTRADOR
# =========================================================


@decorators.rol_requerido(

    "administrador"

)
def dashboard(request):

    return render(

        request,

        "admin/dashboard.html"

    )


# =========================================================
# LISTAR USUARIOS
# =========================================================


@decorators.rol_requerido(

    "administrador"

)
def Listar_usuarios(request):

    usuarios = Usuario.objects.filter(

        rol__nombre__iexact="usuario"

    )


    return render(

        request,

        "admin/usuarios/usuarios.html",

        {

            "usuarios": usuarios

        }

    )


# =========================================================
# EDITAR USUARIO
# =========================================================


@decorators.rol_requerido(

    "administrador"

)
def Editar_usuario(

    request,

    usuario_id

):

    usuario = get_object_or_404(

        Usuario,

        id=usuario_id

    )


    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        usuario_form = EditarUsuarioForm(

            request.POST,

            instance=usuario

        )


        if usuario_form.is_valid():

            usuario_form.save()


            return redirect(

                "listar_usuarios"

            )


    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    else:

        usuario_form = EditarUsuarioForm(

            instance=usuario

        )


    return render(

        request,

        "admin/docente/editar_docente.html",

        {

            "usuario_form":

                usuario_form

        }

    )


# =========================================================
# ELIMINAR USUARIO
# =========================================================


@decorators.rol_requerido(

    "administrador"

)
def Eliminar_usuario(

    request,

    usuario_id

):

    usuario = get_object_or_404(

        Usuario,

        id=usuario_id

    )


    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        usuario.delete()


        return redirect(

            "listar_usuarios"

        )


    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    return render(

        request,

        "admin/docente/eliminar_docente.html",

        {

            "usuario":

                usuario

        }

    )