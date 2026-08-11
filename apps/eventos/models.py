from django.db import models


class Evento(models.Model):

    TIPOS_EVENTO = [
        ("general", "General"),
        ("academico", "Académico"),
        ("reunion", "Reunión"),
        ("evaluacion", "Evaluación"),
        ("actividad", "Actividad"),
        ("aviso", "Aviso"),
    ]

    PUBLICO = [
        ("todos", "Todos"),
        ("alumnos", "Alumnos"),
        ("docentes", "Docentes"),
    ]

    titulo = models.CharField(
        max_length=200
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS_EVENTO,
        default="general"
    )

    fecha = models.DateField()

    hora = models.TimeField(
        null=True,
        blank=True
    )

    descripcion = models.TextField()

    imagen = models.ImageField(
        upload_to="eventos/",
        null=True,
        blank=True
    )

    video = models.URLField(
        blank=True,
        null=True
    )

    publico = models.CharField(
        max_length=20,
        choices=PUBLICO,
        default="todos"
    )

    publicado = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.titulo