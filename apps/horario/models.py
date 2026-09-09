from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.docentes.models import Docente


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
        verbose_name="Fecha de inicio",
        validators=[
            MinValueValidator(
                timezone.localdate,
                message="La fecha de inicio no puede ser anterior a hoy."
            )
        ]
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


class Horario(models.Model):

    DIAS_SEMANA = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miércoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
        ("sabado", "Sábado"),
    ]

    JORNADAS = [
        ("manana", "Mañana"),
        ("tarde", "Tarde"),
    ]

    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name="horarios"
    )

    docente = models.ForeignKey(
        Docente,
        on_delete=models.CASCADE,
        related_name="horarios"
    )

    dia = models.CharField(
        max_length=20,
        choices=DIAS_SEMANA
    )

    jornada = models.CharField(
        max_length=10,
        choices=JORNADAS
    )

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    activo = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "dia",
            "hora_inicio"
        ]

    def __str__(self):
        return (
            f"{self.docente} - "
            f"{self.get_dia_display()} - "
            f"{self.hora_inicio} a {self.hora_fin}"
        )