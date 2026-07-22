from functools import wraps

from django.shortcuts import redirect


# =========================================================
# OBTENER EL PANEL SEGÚN EL ROL
# =========================================================

def obtener_panel_por_rol(rol):

    rol = rol.lower().strip()

    if rol == "administrador":

        return "dashboard_administrador"

    elif rol == "docente":

        return "dashboard_docente"

    elif rol == "alumno":

        return "dashboard_alumno"

    elif rol == "usuario":

        return "verificacion"

    return "index"


# =========================================================
# DECORADOR PARA PROTEGER VISTAS SEGÚN ROL
# =========================================================

def rol_requerido(*roles_permitidos):

    def decorador(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # =================================================
            # 1. USUARIO NO AUTENTICADO
            # =================================================

            if not request.user.is_authenticated:

                return redirect("login")


            # =================================================
            # 2. USUARIO SIN ROL
            # =================================================

            if not request.user.rol:

                return redirect("login")


            # =================================================
            # 3. OBTENER ROL DEL USUARIO
            # =================================================

            rol_usuario = (
                request.user.rol.nombre
                .lower()
                .strip()
            )


            # =================================================
            # 4. NORMALIZAR ROLES PERMITIDOS
            # =================================================

            roles_normalizados = [

                rol.lower().strip()

                for rol in roles_permitidos

            ]


            # =================================================
            # 5. VERIFICAR SI TIENE PERMISO
            # =================================================

            if rol_usuario in roles_normalizados:

                return view_func(
                    request,
                    *args,
                    **kwargs
                )


            # =================================================
            # 6. NO TIENE PERMISO
            # ENVIAR A SU PROPIO PANEL
            # =================================================

            return redirect(
                obtener_panel_por_rol(
                    rol_usuario
                )
            )


        return wrapper


    return decorador