from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.alumnos.models import Alumnos
from apps.clases.models import Clases
from apps.cursos.models import Cursos
from apps.docentes.models import AsignacionDocente, Docente
from apps.horario.models import Periodo
from apps.tareas.models import Calificacion, Tareas
from apps.user.models import Usuario

from apps.boletin.models import ContenidoPedagogico, ObservacionBoletin
from apps.boletin.services import construir_boletin


class ConsolidadoBoletinTests(TestCase):
    def test_solo_incluye_notas_del_periodo_y_contenido_individual(self):
        curso = Cursos.objects.create(nombre="7A")
        materia = Clases.objects.create(titulo="Matemáticas", curso=curso)
        docente_usuario = Usuario.objects.create_user(username="docente", email="d@e.co")
        docente = Docente.objects.create(usuario=docente_usuario, direccion="Dirección")
        asignacion = AsignacionDocente.objects.create(docente=docente, curso=curso, clase=materia)
        alumno_usuario = Usuario.objects.create_user(username="alumno", email="a@e.co")
        alumno = Alumnos.objects.create(usuario=alumno_usuario, curso=curso, clase=materia)
        periodo = Periodo.objects.create(numero=1, anio=2026, fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 3, 31))
        tarea_periodo = Tareas.objects.create(docente=docente, curso=curso, clase=materia, titulo="Dentro", fecha_entrega=date(2026, 2, 15))
        tarea_fuera = Tareas.objects.create(docente=docente, curso=curso, clase=materia, titulo="Fuera", fecha_entrega=date(2026, 4, 15))
        Calificacion.objects.create(alumno=alumno_usuario, tarea=tarea_periodo, nota=Decimal("4.00"))
        Calificacion.objects.create(alumno=alumno_usuario, tarea=tarea_fuera, nota=Decimal("1.00"))
        contenido = ContenidoPedagogico.objects.create(asignacion=asignacion, periodo=periodo, competencias="Razonamiento")
        ObservacionBoletin.objects.create(contenido=contenido, alumno=alumno, observacion="Buen proceso")

        filas, promedio = construir_boletin(alumno, periodo, AsignacionDocente.objects.filter(pk=asignacion.pk))

        self.assertEqual(filas[0]["nota"], Decimal("4.00"))
        self.assertEqual(promedio, Decimal("4.00"))
        self.assertTrue(filas[0]["completo"])
