from django.db import models
from apps.user.models import Usuario
from embed_video.fields import EmbedVideoField
from apps.clases.models import Clases
from apps.cursos.models import Cursos



class Tareas(models.Model):

    titulo = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    fecha_creacion = models.DateField(
        auto_now_add=True
    )

    fecha_entrega = models.DateField(
        blank=True,
        null=True
    )

    clase = models.ForeignKey(
        Clases,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    curso = models.ForeignKey(
        Cursos,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    activa = models.BooleanField(
        default=True
    )

    class Meta:

        verbose_name = "Tarea"

        verbose_name_plural = "Tareas"

    def __str__(self):

        return str(self.titulo)


class Video(models.Model):
    tarea = models.ForeignKey(Tareas, on_delete=models.CASCADE)
    video = EmbedVideoField(blank=True, null=True)


class Imagen(models.Model):
    tarea = models.ForeignKey(Tareas, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(null=True, blank=True, upload_to="imagenes/")

    def __str__(self):
        return str(self.imagen)


class ArchivoTarea(models.Model):
    tarea = models.ForeignKey(
        "Tareas", on_delete=models.CASCADE, related_name="archivos"
    )

    archivo = models.FileField(upload_to="archivos/", blank=True, null=True)

    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tarea} - {self.archivo.name}"


class Pregunta(models.Model):
    TIPOS = (
        ("texto", "Respuesta abierta"),
        ("opcion", "Opción múltiple"),
    )

    tarea = models.ForeignKey(
        Tareas, on_delete=models.CASCADE, related_name="preguntas"
    )

    descripcion = models.TextField(blank=True, null=True)

    tipo = models.CharField(max_length=20, choices=TIPOS)

    puntaje = models.DecimalField(max_digits=3, decimal_places=2, default=1)

    def __str__(self):
        return f" {self.descripcion} - {self.tipo} - puntaje "


class OpcionesRespuesta(models.Model):
    pregunta = models.ForeignKey(
        Pregunta, on_delete=models.CASCADE, related_name="opciones"
    )

    opcion = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.opcion} - {self.es_correcta}"


class RespuestaCorrecta(models.Model):
    pregunta = models.OneToOneField(Pregunta, on_delete=models.CASCADE)

    respuesta = models.CharField("Respuesta", max_length=255)

    def __str__(self):
        return self.respuesta


class RespuestaAlumno(models.Model):

    alumno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE
    )

    respuesta_texto = models.TextField(
        blank=True,
        null=True
    )

    opcion_seleccionada = models.ForeignKey(
        OpcionesRespuesta,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    fecha_respuesta = models.DateTimeField(
        auto_now_add=True
    )

    es_correcta = models.BooleanField(
        default=False
    )

    nota_obtenida = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    calificada = models.BooleanField(
        default=False
    )

class Calificacion(models.Model):
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    tarea = models.ForeignKey(Tareas, on_delete=models.CASCADE)

    nota = models.DecimalField(max_digits=3, decimal_places=2)
