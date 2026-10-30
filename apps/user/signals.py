from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Usuario
from apps.docentes.models import Docente
from apps.alumnos.models import Alumnos, Acudiente


@receiver(pre_save, sender=Usuario)
def recordar_rol_anterior(sender, instance, raw=False, **kwargs):
    """Record the persisted role so ordinary account saves do not sync profiles."""
    if raw or not instance.pk:
        return
    instance._rol_id_anterior = (
        Usuario.objects.filter(pk=instance.pk)
        .values_list("rol_id", flat=True)
        .first()
    )


@receiver(post_save, sender=Usuario)
def sincronizar_perfiles_por_rol(sender, instance, created, raw=False, **kwargs):
    """Create role profiles on creation or a real role change, never delete them."""
    if raw:
        return

    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "rol" not in update_fields:
        return

    rol_anterior = getattr(instance, "_rol_id_anterior", None)
    if not created and rol_anterior == instance.rol_id:
        return

    rol_nombre = (instance.rol.nombre if instance.rol else "").strip().lower()

    if rol_nombre == "docente":
        Docente.objects.get_or_create(usuario=instance)
    elif rol_nombre == "alumno":
        alumno, _ = Alumnos.objects.get_or_create(
            usuario=instance,
            defaults={"fecha_nacimiento": instance.fecha_nacimiento},
        )
        if instance.fecha_nacimiento and alumno.fecha_nacimiento != instance.fecha_nacimiento:
            alumno.fecha_nacimiento = instance.fecha_nacimiento
            alumno.save(update_fields=["fecha_nacimiento"])
        elif alumno.fecha_nacimiento and not instance.fecha_nacimiento:
            Usuario.objects.filter(pk=instance.pk).update(
                fecha_nacimiento=alumno.fecha_nacimiento
            )
            instance.fecha_nacimiento = alumno.fecha_nacimiento
    elif rol_nombre == "acudiente":
        Acudiente.objects.get_or_create(usuario=instance)
