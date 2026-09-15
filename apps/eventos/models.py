from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


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

    hora_inicio = models.TimeField(
        null=True,
        blank=True
    )

    hora_fin = models.TimeField(
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

    def clean(self):
        super().clean()

        hoy = timezone.localdate()
        ahora = timezone.localtime().time()

        # ==========================================
        # FECHA
        # ==========================================

        if self.fecha and self.fecha < hoy:
            raise ValidationError({
                "fecha": "No puedes crear un evento en una fecha que ya pasó."
            })

        # ==========================================
        # VALIDAR HORAS
        # ==========================================

        if self.hora_inicio and self.hora_fin:

            if self.hora_fin <= self.hora_inicio:
                raise ValidationError({
                    "hora_fin": "La hora de finalización debe ser posterior a la hora de inicio."
                })

        # ==========================================
        # SI ES HOY, LA HORA DE INICIO DEBE SER FUTURA
        # ==========================================

        if (
            self.fecha == hoy
            and self.hora_inicio
            and self.hora_inicio <= ahora
        ):
            raise ValidationError({
                "hora_inicio": "No puedes crear un evento con una hora de inicio que ya pasó."
            })

        # ==========================================
        # EVITAR CRUCE DE EVENTOS
        # ==========================================

        if (
            self.fecha
            and self.hora_inicio
            and self.hora_fin
        ):

            eventos = Evento.objects.filter(
                fecha=self.fecha,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            )

            # Si estamos editando un evento, no debe compararse
            # consigo mismo.
            if self.pk:
                eventos = eventos.exclude(pk=self.pk)

            if eventos.exists():

                evento = eventos.first()

                raise ValidationError({
                    "hora_inicio": (
                        f"El horario seleccionado se cruza con otro evento: "
                        f"'{evento.titulo}' "
                        f"({evento.hora_inicio.strftime('%I:%M %p')} - "
                        f"{evento.hora_fin.strftime('%I:%M %p')})."
                    ),
                    "hora_fin": (
                        "Selecciona un horario que no se cruce con otro evento."
                    ),
                })

    def __str__(self):
        return self.titulo