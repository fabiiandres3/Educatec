from django.shortcuts import render, redirect
from django.contrib import messages
from apps.user.models import Usuario, Roles
from apps.user.forms import RegistrarForm, LoginForm
from django.contrib.auth import authenticate, login, logout

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
            password = form.cleaned_data["password"]
            password2 = form.cleaned_data["password2"]

            if password != password2:
                form.add_error("password2", "Las contraseñas no coinciden.")
                return render(request, "user/registrar.html", {"form": form})

            usuario = form.save(commit=False)

            # Username automático usando el correo
            usuario.username = usuario.email

            # Encriptar contraseña
            usuario.set_password(password)

            usuario.save()

            messages.success(request, "Usuario registrado correctamente.")
            return redirect("iniciar_sesion")

    else:
        form = RegistrarForm()

    return render(request, "user/registrar.html", {"form": form})


def iniciar_sesion(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            usuario = authenticate(
                request,
                username=username,
                password=password
            )

            if usuario is not None:
                login(request, usuario)
                return redirect("index")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")

    else:
        form = LoginForm()

    return render(request, "login/login.html", {"form": form})


def cerrar_sesion(request):
    logout(request)
    return redirect("index")


def verificacion(request):
    if request.user.is_authenticated:
        return render(request, "login/verificacion.html")
    
def dashboard(request):
    return render(request, "admin/dashboard.html")
