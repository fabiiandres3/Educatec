from django.test import TestCase

from apps.docentes.forms import DocenteForm
from apps.docentes.models import Docente
from apps.user.models import Usuario


class DocenteTelefonoTests(TestCase):
    def test_guarda_como_texto_un_telefono_mayor_que_integer(self):
        usuario = Usuario.objects.create_user(
            username="docente-telefono",
            email="docente-telefono@example.com",
        )
        docente = Docente.objects.create(
            usuario=usuario,
            telefono="9876543210",
            direccion="Direccion de prueba",
        )

        docente.refresh_from_db()

        self.assertEqual(docente.telefono, "9876543210")
        self.assertIsInstance(docente.telefono, str)

    def test_formulario_usa_entrada_de_texto_para_telefono(self):
        formulario = DocenteForm()

        self.assertEqual(formulario.fields["telefono"].widget.input_type, "text")
