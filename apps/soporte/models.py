from django.conf import settings
from django.db import models


class SolicitudSoporte(models.Model):
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_soporte",
    )
    nombre_solicitante = models.CharField(max_length=255)
    correo_solicitante = models.EmailField()
    rol_solicitante = models.CharField(max_length=100)
    asunto = models.CharField(max_length=120)
    mensaje = models.TextField(max_length=5000)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-creada",)
        verbose_name = "solicitud de soporte"
        verbose_name_plural = "solicitudes de soporte"

    def __str__(self):
        return f"{self.asunto} — {self.correo_solicitante}"
