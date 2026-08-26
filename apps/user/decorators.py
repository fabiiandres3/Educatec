from functools import wraps

from django.shortcuts import redirect


# =========================================================
# OBTENER PANEL SEGÚN ROL
# =========================================================

def obtener_panel_por_rol(rol):

    rol = rol.lower().strip()

    if rol == "administrador":

        return "dashboard_administrador"

    elif rol == "docente":

        return "dashboard_docente"

    elif rol == "alumno":

        return "dashboard_alumnos"

    elif rol == "acudiente":

        return "dashboard_acudiente"

    elif rol == "usuario":

        return "verificacion"

    return "index"


# =========================================================
# DECORADOR DE ROLES
# =========================================================

def rol_requerido(*roles_permitidos):

    def decorador(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # -------------------------------------------------
            # NO AUTENTICADO
            # -------------------------------------------------

            if not request.user.is_authenticated:

                return redirect("login")

            # -------------------------------------------------
            # SIN ROL
            # -------------------------------------------------

            if not request.user.rol:

                return redirect("login")

            # -------------------------------------------------
            # ROL ACTUAL
            # -------------------------------------------------

            rol_usuario = (
                request.user.rol.nombre
                .lower()
                .strip()
            )

            # -------------------------------------------------
            # ROLES PERMITIDOS
            # -------------------------------------------------

            roles_normalizados = [

                rol.lower().strip()

                for rol in roles_permitidos

            ]

            # -------------------------------------------------
            # PERMITIDO
            # -------------------------------------------------

            if rol_usuario in roles_normalizados:

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

            # -------------------------------------------------
            # NO PERMITIDO
            # -------------------------------------------------

            return redirect(
                obtener_panel_por_rol(
                    rol_usuario
                )
            )

        return wrapper

    return decorador