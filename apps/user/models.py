from django.contrib.auth.models import AbstractUser
from django.db import models



class Roles(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    
    rol = models.ForeignKey(Roles,on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField("Nombre", max_length=100)

    last_name = models.CharField("Apellido", max_length=100)

    email = models.EmailField("Correo electrónico")

    password = models.CharField("Contraseña", max_length=100)

    password2 = models.CharField("Confirmar contraseña", max_length=100)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


