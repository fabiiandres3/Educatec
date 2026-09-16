from django.db import models

# Create your models here.
# Esta aplicación utiliza el modelo Calificacion
# que se encuentra en apps.tareas.models.
#
# No se crea un segundo modelo de calificaciones
# para evitar duplicar las notas.

from apps.tareas.models import Calificacion