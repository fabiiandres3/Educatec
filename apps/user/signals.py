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

        alumno, _ = Alumnos.objects.get_or_create(
            usuario=instance,
            defaults={"fecha_nacimiento": instance.fecha_nacimiento},
        )

        # Los alumnos importados antiguamente podían tener la fecha solo
        # en su perfil académico. Conserva ese dato en la cuenta y úsalo
        # al crear o sincronizar el perfil según el rol.
        if instance.fecha_nacimiento and alumno.fecha_nacimiento != instance.fecha_nacimiento:
            alumno.fecha_nacimiento = instance.fecha_nacimiento
            alumno.save(update_fields=["fecha_nacimiento"])
        elif alumno.fecha_nacimiento and not instance.fecha_nacimiento:
            Usuario.objects.filter(pk=instance.pk).update(
                fecha_nacimiento=alumno.fecha_nacimiento
            )
            instance.fecha_nacimiento = alumno.fecha_nacimiento

    else:

        alumno = Alumnos.objects.filter(usuario=instance).only("fecha_nacimiento").first()
        if alumno and alumno.fecha_nacimiento and not instance.fecha_nacimiento:
            Usuario.objects.filter(pk=instance.pk).update(
                fecha_nacimiento=alumno.fecha_nacimiento
            )
            instance.fecha_nacimiento = alumno.fecha_nacimiento

        Alumnos.objects.filter(usuario=instance).delete()


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
