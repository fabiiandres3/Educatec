from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.user.models import Usuario, Roles
from apps.user.forms import RegistrarForm, LoginForm, EditarUsuarioForm
from django.contrib.auth import authenticate, login, logout
from apps.user import decorators

# Create your views here.


def index(request):
    return render(request, "index.html")


def prescolar(request):
    return render(request, "programas/prescolar.html")


def primaria(request):
    return render(request, "programas/primaria.html")


def secundaria(request):
    return render(request, "programas/secundaria.html")


def Registrar_usuario(request):
    if request.method == "POST":
        form = RegistrarForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            password2 = form.cleaned_data["password2"]

            if password != password2:
                form.add_error("password2", "Las contraseñas no coinciden.")
                return render(request, "login/registrar_usuario.html", {"form": form})

            if Usuario.objects.filter(username=username).exists():
                form.add_error("username", "Este nombre de usuario ya existe.")
                return render(request, "login/registrar_usuario.html", {"form": form})

            if Usuario.objects.filter(email=email).exists():
                form.add_error("email", "Este correo ya está registrado.")
                return render(request, "login/registrar_usuario.html", {"form": form})

            try:
                rol_usuario = Roles.objects.get(nombre__iexact="usuario")
            except Roles.DoesNotExist:
                form.add_error(None, "No existe el rol 'usuario'.")
                return render(request, "login/registrar_usuario.html", {"form": form})

            usuario = form.save(commit=False)
            usuario.username = username
            usuario.email = email
            usuario.rol = rol_usuario
            usuario.set_password(password)
            usuario.save()

            messages.success(request, "Usuario registrado correctamente.")
            return redirect("verificacion")

    else:
        form = RegistrarForm()

    return render(request, "login/registrar_usuario.html", {"form": form})


def iniciar_sesion(request):

    if request.user.is_authenticated:
        return redirect("index")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        usuario = authenticate(request=request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)

            messages.success(request, "Bienvenido.")

            return redirect("index")

        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "login/login.html", {"form": form})


def cerrar_sesion(request):
    logout(request)
    return redirect("index")


def verificacion(request):
    return render(request, "login/verificacion.html")


@decorators.redireccionar_por_rol
def index(request):
    pass


@decorators.rol_requerido("administrador")
def dashboard(request):
    return render(request, "admin/dashboard.html")


#####             ADMINISTRADOR               #####################


def Listar_usuarios(request):
    usuarios = Usuario.objects.filter(rol__nombre="usuario")

    return render(request, "admin/usuarios/usuarios.html", {"usuarios": usuarios})


def Editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == "POST":
        usuario_form = EditarUsuarioForm(request.POST, instance=usuario)

        if usuario_form.is_valid():
            usuario_form.save()
            return redirect("listar_docentes")
    else:
        usuario_form = EditarUsuarioForm(instance=usuario)

    return render(
        request,
        "admin/docente/editar_docente.html",
        {
            "usuario_form": usuario_form,
        },
    )


def Eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == "POST":
        usuario.delete()
        return redirect("listar_usuario")

    return render(
        request,
        "admin/docente/eliminar_docente.html",
        {
            "usuario": usuario,
        },
    )
