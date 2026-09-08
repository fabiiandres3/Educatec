from django.db import models

# Create your models here.

class Periodo(models.Model):

    PERIODOS = [
        (1, "Período 1"),
        (2, "Período 2"),
        (3, "Período 3"),
        (4, "Período 4"),
    ]

    numero = models.PositiveSmallIntegerField(
        choices=PERIODOS,
        verbose_name="Período"
    )

    anio = models.PositiveIntegerField(
        verbose_name="Año académico"
    )

    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio"
    )

    fecha_fin = models.DateField(
        verbose_name="Fecha de finalización"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-anio", "numero"]

        verbose_name = "Período"
        verbose_name_plural = "Períodos"

        constraints = [
            models.UniqueConstraint(
                fields=["anio", "numero"],
                name="periodo_unico_por_anio"
            )
        ]

    def __str__(self):
        return f"Período {self.numero} - {self.anio}"