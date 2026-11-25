import smtplib
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.soporte.models import SolicitudSoporte
from apps.user.models import Roles, Usuario


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST_USER="soporte@example.com",
    EMAIL_HOST_PASSWORD="test-app-password",
    DEFAULT_FROM_EMAIL="soporte@example.com",
)
class SolicitudSoporteTests(TestCase):
    def setUp(self):
        admin_role = Roles.objects.create(nombre="administrador")
        student_role = Roles.objects.create(nombre="alumno")
        self.admin = Usuario.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="test-password",
            rol=admin_role,
        )
        self.student = Usuario.objects.create_user(
            username="student",
            email="student@example.com",
            password="test-password",
            rol=student_role,
        )
        self.client.force_login(self.student)

    def post_support_request(self):
        return self.client.post(
            reverse("solicitud_soporte"),
            {
                "asunto": "Problema con calificaciones",
                "mensaje": "No puedo ver mis calificaciones en el panel.",
                "next": "/dashboard_alumnos/",
            },
        )

    def test_sends_support_request_to_admin_and_requester(self):
        response = self.post_support_request()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/dashboard_alumnos/")
        self.assertIn(
            "Reporte enviado correctamente.",
            [str(message) for message in get_messages(response.wsgi_request)],
        )
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "[Soporte Educatec] Problema con calificaciones")
        self.assertEqual(sent_email.from_email, "soporte@example.com")
        self.assertEqual(sent_email.reply_to, ["student@example.com"])
        self.assertIn("admin@example.com", sent_email.recipients())
        self.assertIn("student@example.com", sent_email.recipients())
        self.assertEqual(SolicitudSoporte.objects.count(), 1)

    @override_settings(EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD="")
    def test_saves_and_shows_request_to_admin_without_smtp(self):
        response = self.post_support_request()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/dashboard_alumnos/")
        self.assertIn(
            "Reporte enviado correctamente.",
            [str(message) for message in get_messages(response.wsgi_request)],
        )
        self.assertEqual(mail.outbox, [])
        self.assertEqual(SolicitudSoporte.objects.count(), 1)

        self.client.force_login(self.admin)
        inbox_response = self.client.get(reverse("notificaciones_correo_admin"))

        self.assertEqual(inbox_response.status_code, 200)
        inbox = inbox_response.json()
        self.assertEqual(inbox["unread_count"], 1)
        self.assertEqual(inbox["emails"][0]["message"], "No puedo ver mis calificaciones en el panel.")

    @patch(
        "apps.soporte.views.EmailMessage.send",
        side_effect=smtplib.SMTPAuthenticationError(535, b"Invalid credentials"),
    )
    def test_reports_smtp_delivery_failure(self, send_email):
        response = self.post_support_request()

        self.assertEqual(response.status_code, 302)
        notification_messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn("Reporte enviado correctamente.", notification_messages)
        self.assertTrue(any("no se pudo enviar la notificación por correo" in message for message in notification_messages))
        self.assertEqual(mail.outbox, [])
        self.assertEqual(SolicitudSoporte.objects.count(), 1)
