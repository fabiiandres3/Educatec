# apps/paneles/models.py
#
# Modelos propios de la app "paneles", pensados para un colegio
# colombiano (escala de notas 1.0 - 5.0, desempeño según el Decreto
# 1290 de 2009: Superior / Alto / Básico / Bajo, y 4 períodos
# académicos por año escolar).
#
# NO hay sistema de roles ni de login: docente y alumnos son
# simples registros de datos que administra quien tenga acceso al
# admin de Django (o a las vistas que construyas). No dependen de
# ningún modelo de Usuario ni de auth.
#
# Todo vive en esta misma app, así que no se toca nada de tus
# compañeros ni de otras apps del proyecto.

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# ---------------------------------------------------------------------------
# CURSO (lo que en un colegio colombiano se conoce como "Grado")
# ---------------------------------------------------------------------------
class Curso(models.Model):
    """
    Un curso es un grado + grupo concreto, ej: "Sexto A", "Once B".
    Se guarda el año escolar para poder llevar historial de cursos
    de un año a otro sin perder los datos anteriores.
    """

    GRADOS = [
        ('prejardin', 'Prejardín'),
        ('jardin', 'Jardín'),
        ('transicion', 'Transición'),
        ('primero', 'Primero'),
        ('segundo', 'Segundo'),
        ('tercero', 'Tercero'),
        ('cuarto', 'Cuarto'),
        ('quinto', 'Quinto'),
        ('sexto', 'Sexto'),
        ('septimo', 'Séptimo'),
        ('octavo', 'Octavo'),
        ('noveno', 'Noveno'),
        ('decimo', 'Décimo'),
        ('once', 'Undécimo'),
    ]

    JORNADAS = [
        ('manana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('unica', 'Única'),
    ]

    grado = models.CharField(max_length=20, choices=GRADOS)
    grupo = models.CharField(max_length=5, default='A')  # A, B, C...
    jornada = models.CharField(max_length=10, choices=JORNADAS, default='unica')
    anio_escolar = models.PositiveIntegerField(help_text='Ej: 2026')

    # Director de grupo (opcional). Se define más abajo, por eso el
    # string 'docente' en lugar de la clase directamente.
    director_grupo = models.ForeignKey(
        'docente', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cursos_dirigidos'
    )

    @property
    def nombre(self):
        """Ej: 'Sexto A'. Se usa en casi todos los templates."""
        return f"{self.get_grado_display()} {self.grupo}"

    def __str__(self):
        return f"{self.nombre} ({self.anio_escolar})"

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        unique_together = ('grado', 'grupo', 'anio_escolar')
        ordering = ['anio_escolar', 'grado', 'grupo']


# ---------------------------------------------------------------------------
# MATERIA
# ---------------------------------------------------------------------------
class Materia(models.Model):
    """
    Asignatura del plan de estudios. El campo 'area' es opcional pero
    útil para agrupar materias por área obligatoria (MEN).
    """

    AREAS = [
        ('ciencias_naturales', 'Ciencias Naturales'),
        ('ciencias_sociales', 'Ciencias Sociales'),
        ('matematicas', 'Matemáticas'),
        ('humanidades', 'Humanidades y Lengua Castellana'),
        ('idioma_extranjero', 'Idioma Extranjero'),
        ('educacion_artistica', 'Educación Artística'),
        ('educacion_fisica', 'Educación Física'),
        ('educacion_religiosa', 'Educación Religiosa'),
        ('etica_valores', 'Ética y Valores'),
        ('tecnologia_informatica', 'Tecnología e Informática'),
        ('otra', 'Otra'),
    ]

    nombre = models.CharField(max_length=100)
    area = models.CharField(max_length=30, choices=AREAS, default='otra')
    intensidad_horaria_semanal = models.PositiveSmallIntegerField(
        default=1, help_text='Horas de clase por semana'
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['nombre']


# ---------------------------------------------------------------------------
# docente
# ---------------------------------------------------------------------------
class docente(models.Model):
    """
    Registro de datos del docente. Sin login: no está ligado a
    ningún modelo de usuario/autenticación.
    """

    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=2, choices=TIPOS_DOCUMENTO, default='CC')
    numero_documento = models.CharField(max_length=20, unique=True)

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)

    titulo_profesional = models.CharField(
        max_length=150, blank=True,
        help_text='Ej: Licenciado en Matemáticas'
    )
    fecha_ingreso = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    @property
    def nombre(self):
        """Nombre completo, usado en todos los templates como docente.nombre."""
        return f"{self.nombres} {self.apellidos}"

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'docente'
        verbose_name_plural = 'docentees'
        ordering = ['apellidos', 'nombres']


# ---------------------------------------------------------------------------
# alumnos
# ---------------------------------------------------------------------------
class alumnos(models.Model):
    """
    Registro de datos del alumnos. Sin login. Incluye datos
    básicos del acudiente porque en Colombia siempre se requieren
    para el boletín / reportes / citaciones.
    """

    TIPOS_DOCUMENTO = [
        ('RC', 'Registro Civil'),
        ('TI', 'Tarjeta de Identidad'),
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PPT', 'Permiso por Protección Temporal'),
    ]

    tipo_documento = models.CharField(max_length=4, choices=TIPOS_DOCUMENTO, default='TI')
    numero_documento = models.CharField(max_length=20, unique=True)

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='alumnoss'
    )

    # Datos básicos del acudiente
    nombre_acudiente = models.CharField(max_length=150, blank=True)
    telefono_acudiente = models.CharField(max_length=20, blank=True)
    correo_acudiente = models.EmailField(blank=True)

    fecha_matricula = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    @property
    def nombre(self):
        """Nombre completo, usado en todos los templates como alumnos.nombre."""
        return f"{self.nombres} {self.apellidos}"

    def __str__(self):
        return f"{self.nombre} - {self.curso.nombre}"

    class Meta:
        verbose_name = 'alumnos'
        verbose_name_plural = 'alumnoss'
        ordering = ['apellidos', 'nombres']


# ---------------------------------------------------------------------------
# ASIGNACIÓN docente (docente + materia + curso)
# ---------------------------------------------------------------------------
class Asignaciondocente(models.Model):
    """
    Un docente dicta una materia en un curso específico. Es la
    tabla puente que usan Calificacion, Asistencia y Tarea para
    saber "quién enseña qué, a quién".
    """

    docente = models.ForeignKey(
        docente, on_delete=models.CASCADE, related_name='asignaciones'
    )
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE, related_name='asignaciones'
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='asignaciones'
    )

    def __str__(self):
        return f"{self.docente} — {self.materia} — {self.curso}"

    class Meta:
        verbose_name = 'Asignación de docente'
        verbose_name_plural = 'Asignaciones de docentees'
        unique_together = ('docente', 'materia', 'curso')


# ---------------------------------------------------------------------------
# PERÍODO ACADÉMICO
# ---------------------------------------------------------------------------
class PeriodoAcademico(models.Model):
    """
    Los colegios colombianos suelen manejar 4 períodos por año
    escolar. Solo puede haber un período activo a la vez (se
    desactivan los demás automáticamente al guardar).
    """

    nombre = models.CharField(max_length=50)  # Ej: "Período I"
    numero = models.PositiveSmallIntegerField(default=1)  # 1, 2, 3, 4
    anio_escolar = models.PositiveIntegerField(help_text='Ej: 2026')
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.activo:
            PeriodoAcademico.objects.exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} — {self.anio_escolar}"

    class Meta:
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'
        ordering = ['anio_escolar', 'numero']
        unique_together = ('numero', 'anio_escolar')


# ---------------------------------------------------------------------------
# CALIFICACIÓN
# ---------------------------------------------------------------------------
class Calificacion(models.Model):
    """
    Nota de un alumnos en una asignación (docente+materia+curso)
    durante un período. Escala colombiana estándar: 1.0 a 5.0.
    El promedio determina el desempeño según el Decreto 1290:
        >= 4.5  Superior
        >= 4.0  Alto
        >= 3.0  Básico
        <  3.0  Bajo
    """

    NOTA_VALIDATORS = [MinValueValidator(0.0), MaxValueValidator(5.0)]

    alumnos = models.ForeignKey(
        alumnos, on_delete=models.CASCADE, related_name='calificaciones'
    )
    asignacion = models.ForeignKey(
        Asignaciondocente, on_delete=models.CASCADE, related_name='calificaciones'
    )
    periodo = models.ForeignKey(
        PeriodoAcademico, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='calificaciones'
    )

    tarea = models.DecimalField(
        max_digits=3, decimal_places=1, default=0, validators=NOTA_VALIDATORS
    )
    parcial = models.DecimalField(
        max_digits=3, decimal_places=1, default=0, validators=NOTA_VALIDATORS
    )
    examen = models.DecimalField(
        max_digits=3, decimal_places=1, default=0, validators=NOTA_VALIDATORS
    )

    fecha_registro = models.DateTimeField(auto_now=True)

    @property
    def promedio(self):
        return round((self.tarea + self.parcial + self.examen) / 3, 1)

    @property
    def desempeno(self):
        prom = self.promedio
        if prom >= 4.5:
            return 'Superior'
        if prom >= 4.0:
            return 'Alto'
        if prom >= 3.0:
            return 'Básico'
        return 'Bajo'

    # Accesos rápidos, para no tener que escribir cal.asignacion.materia
    # en cada template.
    @property
    def materia(self):
        return self.asignacion.materia

    @property
    def docente(self):
        return self.asignacion.docente

    @property
    def curso(self):
        return self.asignacion.curso

    def __str__(self):
        return f"{self.alumnos} — {self.materia}: {self.promedio} ({self.desempeno})"

    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ('alumnos', 'asignacion', 'periodo')


# ---------------------------------------------------------------------------
# ASISTENCIA
# ---------------------------------------------------------------------------
class Asistencia(models.Model):
    """
    Registro diario de asistencia de un alumnos. 'asignacion' es
    opcional porque muchos colegios registran la asistencia general
    del curso en la jornada, sin discriminar por materia.
    """

    ESTADOS = [
        ('presente', 'Presente'),
        ('tardanza', 'Tardanza'),
        ('ausente', 'Ausente'),
        ('excusa', 'Ausencia Justificada'),
    ]

    alumnos = models.ForeignKey(
        alumnos, on_delete=models.CASCADE, related_name='asistencias'
    )
    asignacion = models.ForeignKey(
        Asignaciondocente, on_delete=models.CASCADE,
        null=True, blank=True, related_name='asistencias'
    )
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='presente')
    observacion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.alumnos} — {self.fecha}: {self.get_estado_display()}"

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ('alumnos', 'asignacion', 'fecha')
        ordering = ['-fecha']


# ---------------------------------------------------------------------------
# TAREA (actividad académica con fecha límite y estado de entrega)
# ---------------------------------------------------------------------------
class Tarea(models.Model):
    """
    Tarea/actividad asignada por un docente a un curso, dentro de
    una materia y período. Distinta de una "Calificación": aquí solo
    se controla el enunciado y el estado de entrega, no la nota.
    """

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('entregada', 'Entregada'),
        ('vencida', 'Vencida'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)

    asignacion = models.ForeignKey(
        Asignaciondocente, on_delete=models.CASCADE, related_name='tareas'
    )
    periodo = models.ForeignKey(
        PeriodoAcademico, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tareas'
    )

    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    entregas = models.PositiveIntegerField(default=0)
    total_alumnoss = models.PositiveIntegerField(default=0)

    @property
    def materia(self):
        return self.asignacion.materia

    @property
    def curso(self):
        return self.asignacion.curso

    @property
    def docente(self):
        return self.asignacion.docente

    def __str__(self):
        return f"{self.titulo} — {self.curso}"

    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['fecha_limite']