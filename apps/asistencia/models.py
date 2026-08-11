from django.db import models
from apps.alumnos.models import Alumnos
from apps.cursos.models import Cursos


class Asistencia(models.Model):
    ESTADOS = (
        ("P", "Presente"),
        ("T", "Tardanza"),
        ("A", "Ausente"),
    )

    alumno = models.ForeignKey(Alumnos, on_delete=models.CASCADE, related_name="asistencias")
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(max_length=1, choices=ESTADOS, default="P")

    class Meta:
        unique_together = ("alumno", "fecha")
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"

    def _str_(self):
        return f"{self.alumno} - {self.fecha} - {self.get_estado_display()}"