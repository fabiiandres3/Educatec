from functools import wraps
from django.shortcuts import redirect


def redireccionar_por_rol(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # Verificar autenticación
        if not request.user.is_authenticated:
            return redirect("login")

        # Verificar que tenga rol
        if not request.user.rol:
            return redirect("login")

        # Obtener rol
        rol = request.user.rol.nombre.lower()

        # Redireccionar según el rol
        if rol == "administrador":
            return redirect("dashboard_administrador")

        """elif rol == "docente":
            return redirect("panel_docente")

        elif rol == "alumno":
            return redirect("panel_alumno")

        elif rol == "usuario":
            return redirect("panel_usuario")"""

        return redirect("login")

    return wrapper


def rol_requerido(*roles_permitidos):

    def decorador(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # Usuario no autenticado
            if not request.user.is_authenticated:
                return redirect("login")

            # Usuario sin rol
            if not request.user.rol:
                return redirect("login")

            # Obtener rol
            rol = request.user.rol.nombre.lower()

            # Verificar permiso
            if rol in roles_permitidos:
                return view_func(request, *args, **kwargs)

            # Si no tiene permiso, devolverlo a su panel
            if rol == "administrador":
                return redirect("dashboard_administrador")

            """elif rol == "docente":
                return redirect("panel_docente")

            elif rol == "alumno":
                return redirect("panel_alumno")

            elif rol == "usuario":
                return redirect("verificacion")"""

            return redirect("login")

        return wrapper

    return decorador