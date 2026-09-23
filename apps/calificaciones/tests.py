from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.alumnos.models import Alumnos
from apps.clases.models import Clases
from apps.cursos.models import Cursos
from apps.docentes.models import AsignacionDocente, Docente
from apps.tareas.models import Calificacion, Pregunta, RespuestaAlumno, Tareas
from apps.user.models import Usuario

from .services import obtener_libro_calificaciones


class CalificacionesPorAsignacionTests(TestCase):
    def setUp(self):
        self.curso = Cursos.objects.create(nombre="Curso compartido")
        self.matematicas = Clases.objects.create(titulo="Matemáticas", curso=self.curso)
        self.ciencias = Clases.objects.create(titulo="Ciencias", curso=self.curso)
        self.docente_matematicas = Docente.objects.create(
            usuario=Usuario.objects.create_user(username="mate", email="mate@example.com"),
            direccion="Dirección",
        )
        self.docente_ciencias = Docente.objects.create(
            usuario=Usuario.objects.create_user(username="ciencias", email="ciencias@example.com"),
            direccion="Dirección",
        )
        self.asignacion_matematicas = AsignacionDocente.objects.create(
            docente=self.docente_matematicas, curso=self.curso, clase=self.matematicas,
        )
        self.asignacion_ciencias = AsignacionDocente.objects.create(
            docente=self.docente_ciencias, curso=self.curso, clase=self.ciencias,
        )
        self.alumno_usuario = Usuario.objects.create_user(username="alumno", email="alumno@example.com")
        Alumnos.objects.create(usuario=self.alumno_usuario, curso=self.curso, activo=True)

    def test_cada_docente_ve_solo_su_materia_en_el_mismo_curso(self):
        tarea_mate = Tareas.objects.create(
            docente=self.docente_matematicas, curso=self.curso, clase=self.matematicas, titulo="Álgebra",
        )
        tarea_ciencias = Tareas.objects.create(
            docente=self.docente_ciencias, curso=self.curso, clase=self.ciencias, titulo="Biología",
        )
        Calificacion.objects.create(alumno=self.alumno_usuario, tarea=tarea_mate, nota=Decimal("4.50"))
        Calificacion.objects.create(alumno=self.alumno_usuario, tarea=tarea_ciencias, nota=Decimal("3.50"))

        _, tareas_mate, _ = obtener_libro_calificaciones(self.asignacion_matematicas)
        _, tareas_ciencias, _ = obtener_libro_calificaciones(self.asignacion_ciencias)

        self.assertEqual([tarea.id for tarea in tareas_mate], [tarea_mate.id])
        self.assertEqual([tarea.id for tarea in tareas_ciencias], [tarea_ciencias.id])

    def test_muestra_notas_de_tareas_heredadas_o_deshabilitadas(self):
        tarea_heredada = Tareas.objects.create(
            docente=self.docente_ciencias,
            curso=self.curso,
            clase=None,
            titulo="Tarea antigua de Inglés",
            activa=False,
        )
        Calificacion.objects.create(
            alumno=self.alumno_usuario,
            tarea=tarea_heredada,
            nota=Decimal("4.00"),
        )

        _, tareas, _ = obtener_libro_calificaciones(self.asignacion_ciencias)

        self.assertEqual([tarea.id for tarea in tareas], [tarea_heredada.id])

    def test_botones_de_revision_actualizan_la_calificacion_final(self):
        tarea = Tareas.objects.create(
            docente=self.docente_matematicas, curso=self.curso, clase=self.matematicas, titulo="Ejercicio",
        )
        pregunta = Pregunta.objects.create(tarea=tarea, descripcion="Resuelve", tipo="texto", puntaje=Decimal("5.00"))
        respuesta = RespuestaAlumno.objects.create(alumno=self.alumno_usuario, pregunta=pregunta, respuesta_texto="respuesta")
        self.client.force_login(self.docente_matematicas.usuario)

        self.client.post(reverse("evaluar_respuesta", args=[tarea.id]), {
            "respuesta_id": respuesta.id, "estado": "correct", "nota": "0",
        })
        respuesta.refresh_from_db()
        self.assertTrue(respuesta.calificada)
        self.assertTrue(respuesta.es_correcta)
        self.assertEqual(respuesta.nota_obtenida, Decimal("5.00"))
        self.assertEqual(Calificacion.objects.get(alumno=self.alumno_usuario, tarea=tarea).nota, Decimal("5.00"))

        self.client.post(reverse("evaluar_respuesta", args=[tarea.id]), {
            "respuesta_id": respuesta.id, "estado": "incorrect", "nota": "2",
        })
        respuesta.refresh_from_db()
        self.assertEqual(respuesta.nota_obtenida, Decimal("2.00"))
        self.assertEqual(Calificacion.objects.get(alumno=self.alumno_usuario, tarea=tarea).nota, Decimal("2.00"))
