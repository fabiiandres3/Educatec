from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class Roles(models.Model):

    nombre = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):

    rol = models.ForeignKey(
        Roles,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True
    )

    documento = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    telefono = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name="fecha de nacimiento",
    )

    def save(self, *args, **kwargs):
        # username es el identificador de inicio de sesión y también el
        # documento de identidad que consulta el resto del sistema.
        self.documento = self.username
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"documento"}
        super().save(*args, **kwargs)

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None

        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return self.documento or self.username
