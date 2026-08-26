from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Usuario

from apps.docentes.models import Docente

from apps.alumnos.models import (
    Alumnos,
    Acudiente,
)


# =========================================================
# DOCENTE
# =========================================================

@receiver(post_save, sender=Usuario)
def sincronizar_docente(
    sender,
    instance,
    **kwargs
):

    if (
        instance.rol
        and instance.rol.nombre.lower().strip() == "docente"
    ):

        Docente.objects.get_or_create(
            usuario=instance
        )

    else:

        Docente.objects.filter(
            usuario=instance
        ).delete()


# =========================================================
# ALUMNO
# =========================================================

@receiver(post_save, sender=Usuario)
def sincronizar_alumno(
    sender,
    instance,
    **kwargs
):

    if (
        instance.rol
        and instance.rol.nombre.lower().strip() == "alumno"
    ):

        Alumnos.objects.get_or_create(
            usuario=instance
        )

    else:

        Alumnos.objects.filter(
            usuario=instance
        ).delete()


# =========================================================
# ACUDIENTE
# =========================================================

@receiver(post_save, sender=Usuario)
def sincronizar_acudiente(
    sender,
    instance,
    **kwargs
):

    if (
        instance.rol
        and instance.rol.nombre.lower().strip() == "acudiente"
    ):

        Acudiente.objects.get_or_create(
            usuario=instance
        )

    else:

        Acudiente.objects.filter(
            usuario=instance
        ).delete()