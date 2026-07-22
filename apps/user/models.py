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
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    def __str__(self):
        return self.username