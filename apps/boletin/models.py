from django.db import models


class ContenidoPedagogico(models.Model):
    """Información común de una asignación durante un período."""

    asignacion = models.ForeignKey(
        "docentes.AsignacionDocente", on_delete=models.CASCADE,
        related_name="contenidos_boletin"
    )
    periodo = models.ForeignKey(
        "horario.Periodo", on_delete=models.CASCADE,
        related_name="contenidos_boletin"
    )
    competencias = models.TextField(blank=True)
    contenidos = models.TextField(blank=True)
    logros = models.TextField(blank=True)
    dificultades_generales = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["asignacion", "periodo"],
            name="contenido_boletin_unico_por_asignacion_periodo",
        )]
        ordering = ["periodo__anio", "periodo__numero", "asignacion__id"]
        verbose_name = "Contenido pedagógico"
        verbose_name_plural = "Contenidos pedagógicos"

    def __str__(self):
        return f"{self.asignacion} — {self.periodo}"


class ObservacionBoletin(models.Model):
    """Comentario individual: nunca se comparte entre estudiantes."""

    contenido = models.ForeignKey(
        ContenidoPedagogico, on_delete=models.CASCADE,
        related_name="observaciones"
    )
    alumno = models.ForeignKey(
        "alumnos.Alumnos", on_delete=models.CASCADE,
        related_name="observaciones_boletin"
    )
    observacion = models.TextField(blank=True)
    publicado = models.BooleanField(
        default=False,
        help_text="Visible para el alumno dentro de su boletín consolidado.",
    )
    publicado_en = models.DateTimeField(blank=True, null=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["contenido", "alumno"],
            name="observacion_boletin_unica_por_alumno_contenido",
        )]
        verbose_name = "Observación de boletín"
        verbose_name_plural = "Observaciones de boletín"

    def __str__(self):
        return f"{self.alumno} — {self.contenido}"
