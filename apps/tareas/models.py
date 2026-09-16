from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.user.models import Usuario
from embed_video.fields import EmbedVideoField
from apps.clases.models import Clases
from apps.cursos.models import Cursos
from apps.docentes.models import Docente


# ============================================================
# TAREAS
# ============================================================

class Tareas(models.Model):

    docente = models.ForeignKey(
        "docentes.Docente",
        on_delete=models.CASCADE,
        related_name="tareas",
        null=True,
        blank=True
    )

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

    def clean(self):
        super().clean()

        # ----------------------------------------------------
        # FECHA DE ENTREGA NO PUEDE SER ANTERIOR A HOY
        # ----------------------------------------------------

        if (
            self.fecha_entrega
            and self.fecha_entrega < timezone.localdate()
        ):
            raise ValidationError({
                "fecha_entrega":
                    "No puedes establecer una fecha de entrega que ya pasó."
            })

        # ----------------------------------------------------
        # FECHA DE ENTREGA NO PUEDE SER ANTERIOR
        # A LA FECHA DE CREACIÓN
        # ----------------------------------------------------

        if (
            self.fecha_entrega
            and self.fecha_creacion
            and self.fecha_entrega < self.fecha_creacion
        ):
            raise ValidationError({
                "fecha_entrega":
                    "La fecha de entrega no puede ser anterior a la fecha de creación."
            })

    def __str__(self):
        return self.titulo


# ============================================================
# TAREA - ALUMNO
# ============================================================

class TareaAlumno(models.Model):

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE,
        related_name="alumnos_estado"
    )

    alumno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="tareas_estado"
    )

    activa = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = (
            "tarea",
            "alumno"
        )

    def __str__(self):
        return f"{self.tarea} - {self.alumno}"


# ============================================================
# VIDEO
# ============================================================

class Video(models.Model):

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE
    )

    video = EmbedVideoField(
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.video)


# ============================================================
# IMAGEN
# ============================================================

class Imagen(models.Model):

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE,
        related_name="imagenes"
    )

    imagen = models.ImageField(
        null=True,
        blank=True,
        upload_to="imagenes/"
    )

    def __str__(self):
        return str(self.imagen)


# ============================================================
# ARCHIVO DE TAREA
# ============================================================

class ArchivoTarea(models.Model):

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE,
        related_name="archivos"
    )

    archivo = models.FileField(
        upload_to="archivos/",
        blank=True,
        null=True
    )

    fecha_subida = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.tarea} - {self.archivo.name}"


# ============================================================
# PREGUNTA
# ============================================================

class Pregunta(models.Model):

    TIPOS = (
        ("texto", "Respuesta abierta"),
        ("opcion", "Opción múltiple"),
    )

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE,
        related_name="preguntas"
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    puntaje = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1
    )

    def __str__(self):
        return f"{self.descripcion} - {self.tipo} - puntaje"


# ============================================================
# OPCIONES DE RESPUESTA
# ============================================================

class OpcionesRespuesta(models.Model):

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="opciones"
    )

    opcion = models.CharField(
        max_length=255
    )

    es_correcta = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.opcion} - {self.es_correcta}"


# ============================================================
# RESPUESTA CORRECTA
# ============================================================

class RespuestaCorrecta(models.Model):

    pregunta = models.OneToOneField(
        Pregunta,
        on_delete=models.CASCADE
    )

    respuesta = models.CharField(
        "Respuesta",
        max_length=255
    )

    def __str__(self):
        return self.respuesta


# ============================================================
# RESPUESTA DEL ALUMNO
# ============================================================

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

    def __str__(self):
        return f"{self.alumno} - {self.pregunta}"


# ============================================================
# CALIFICACIÓN FINAL DE LA TAREA
# ============================================================

class Calificacion(models.Model):

    alumno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE
    )

    nota = models.DecimalField(
        max_digits=3,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "tarea"],
                name="unique_calificacion_alumno_tarea"
            )
        ]

    def __str__(self):
        return f"{self.alumno} - {self.tarea} - {self.nota}"
    
    # ============================================================
# CALIFICACIÓN FINAL DE LA TAREA
# ============================================================

class Calificacion(models.Model):

    alumno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE
    )

    nota = models.DecimalField(
        max_digits=3,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "tarea"],
                name="unique_calificacion_alumno_tarea"
            )
        ]

    def __str__(self):
        return f"{self.alumno} - {self.tarea} - {self.nota}"


# ============================================================
# ACTIVIDADES MANUALES DE CALIFICACIÓN
# ============================================================

class ActividadCalificacion(models.Model):

    docente = models.ForeignKey(
        "docentes.Docente",
        on_delete=models.CASCADE,
        related_name="actividades_calificacion"
    )

    curso = models.ForeignKey(
        "cursos.Cursos",
        on_delete=models.CASCADE,
        related_name="actividades_calificacion"
    )

    clase = models.ForeignKey(
        "clases.Clases",
        on_delete=models.CASCADE,
        related_name="actividades_calificacion"
    )

    nombre = models.CharField(
        max_length=150
    )

    tipo = models.CharField(
        max_length=50,
        default="Actividad"
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    fecha = models.DateField(
        auto_now_add=True
    )

    activa = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["fecha", "id"]
        verbose_name = "Actividad de calificación"
        verbose_name_plural = "Actividades de calificación"

    def __str__(self):
        return self.nombre


# ============================================================
# CALIFICACIÓN DE ACTIVIDAD MANUAL
# ============================================================

class CalificacionActividad(models.Model):

    actividad = models.ForeignKey(
        ActividadCalificacion,
        on_delete=models.CASCADE,
        related_name="calificaciones"
    )

    alumno = models.ForeignKey(
        "user.Usuario",
        on_delete=models.CASCADE,
        related_name="calificaciones_actividades"
    )

    nota = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actividad", "alumno"],
                name="unique_calificacion_actividad_alumno"
            )
        ]

        verbose_name = "Calificación de actividad"
        verbose_name_plural = "Calificaciones de actividades"

    def __str__(self):
        return f"{self.alumno} - {self.actividad} - {self.nota}"