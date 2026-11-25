def notificaciones_no_leidas(request):
    if not request.user.is_authenticated:
        return {"notificaciones_sin_leer": 0}
    from .models import Notificacion
    return {
        "notificaciones_sin_leer": Notificacion.objects.filter(
            usuario=request.user,
            leida=False,
        ).count()
    }
