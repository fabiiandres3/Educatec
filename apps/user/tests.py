import json
import tempfile
from pathlib import Path

from django.core import serializers
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.alumnos.models import Alumnos
from apps.clases.models import Clases
from apps.cursos.models import Cursos
from apps.docentes.models import AsignacionDocente, Docente
from apps.user.models import Roles, Usuario


class SincronizacionPerfilesUsuarioTests(TestCase):
    def test_guardar_campos_de_cuenta_no_elimina_perfil(self):
        usuario = Usuario.objects.create_user(
            username="docente-campos", email="docente-campos@example.com"
        )
        perfil = Docente.objects.create(usuario=usuario, direccion="DirecciÃ³n")

        usuario.email = "nuevo@example.com"
        usuario.first_name = "Nombre actualizado"
        usuario.set_unusable_password()
        usuario.save()
        usuario.last_login = timezone.now()
        usuario.save(update_fields=["last_login"])

        rol_alumno = Roles.objects.create(nombre="alumno")
        usuario.rol = rol_alumno
        usuario.save(update_fields=["email"])

        self.assertTrue(Docente.objects.filter(pk=perfil.pk).exists())
        self.assertFalse(Alumnos.objects.filter(usuario_id=usuario.pk).exists())

    def test_cambio_explicito_de_rol_conserva_perfil_y_asignaciones(self):
        rol_docente = Roles.objects.create(nombre="docente")
        rol_alumno = Roles.objects.create(nombre="alumno")
        usuario = Usuario.objects.create_user(
            username="transicion", email="transicion@example.com", rol=rol_docente
        )
        perfil_docente = Docente.objects.get(usuario=usuario)
        curso = Cursos.objects.create(nombre="Curso conservado")
        clase = Clases.objects.create(titulo="Materia conservada")
        asignacion = AsignacionDocente.objects.create(
            docente=perfil_docente, curso=curso, clase=clase
        )

        usuario.rol = rol_alumno
        usuario.save(update_fields=["rol"])

        self.assertTrue(Docente.objects.filter(pk=perfil_docente.pk).exists())
        self.assertTrue(AsignacionDocente.objects.filter(pk=asignacion.pk).exists())
        self.assertTrue(Alumnos.objects.filter(usuario=usuario).exists())

    def test_loaddata_no_duplica_perfil_docente(self):
        rol = Roles.objects.create(nombre="docente")
        usuario = Usuario.objects.create_user(
            username="origen-fixture", email="origen-fixture@example.com", rol=rol
        )
        perfil = Docente.objects.get(usuario=usuario)
        perfil.direccion = "Perfil origen"
        perfil.save(update_fields=["direccion"])

        datos = json.loads(serializers.serialize("json", [rol, usuario, perfil]))
        ids = {"rol": 91001, "usuario": 91002, "docente": 91003}
        for objeto in datos:
            if objeto["model"] == "user.roles":
                objeto["pk"] = ids["rol"]
            elif objeto["model"] == "user.usuario":
                objeto["pk"] = ids["usuario"]
                objeto["fields"]["username"] = "fixture-docente"
                objeto["fields"]["documento"] = "fixture-docente"
                objeto["fields"]["email"] = "fixture-docente@example.com"
                objeto["fields"]["rol"] = ids["rol"]
            elif objeto["model"] == "docentes.docente":
                objeto["pk"] = ids["docente"]
                objeto["fields"]["usuario"] = ids["usuario"]

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "perfiles.json"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            call_command("loaddata", str(ruta), verbosity=0)

        self.assertEqual(Docente.objects.filter(usuario_id=ids["usuario"]).count(), 1)
        self.assertEqual(
            Docente.objects.get(usuario_id=ids["usuario"]).direccion,
            "Perfil origen",
        )
