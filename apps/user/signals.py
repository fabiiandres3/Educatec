from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Usuario
from apps.docentes.models import Docente
from apps.alumnos.models import Alumnos

@receiver(post_save, sender=Usuario)
def crear_docente(sender, instance, created, **kwargs):
    if instance.rol and instance.rol.nombre.lower() == "docente":
        Docente.objects.get_or_create(usuario=instance)

@receiver(post_save, sender=Usuario)
def sincronizar_docente(sender, instance, **kwargs):
    if instance.rol and instance.rol.nombre.lower() == "docente":
        Docente.objects.get_or_create(usuario=instance)
    else:
        Docente.objects.filter(usuario=instance).delete()

@receiver(post_save, sender=Usuario)
def crear_alumno(sender, instance, created, **kwargs):
    if instance.rol and instance.rol.nombre.lower() == "alumno":
        Docente.objects.get_or_create(usuario=instance)

@receiver(post_save, sender=Usuario)
def sincronizar_alumno(sender, instance, **kwargs):
    if instance.rol and instance.rol.nombre.lower() == "alumno":
        Alumnos.objects.get_or_create(usuario=instance)
    else:
        Alumnos.objects.filter(usuario=instance).delete()