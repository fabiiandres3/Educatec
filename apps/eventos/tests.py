from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, storages
from django.test import SimpleTestCase, override_settings
from storages.backends.s3 import S3Storage
from unittest.mock import Mock, patch

from urllib.parse import urlparse, parse_qs

from apps.eventos.storage import (
    EventoImageStorageRouter,
    build_event_image_storage_config,
)
from apps.eventos.views import crear_evento


class EventoAccessTests(SimpleTestCase):
    def test_anonymous_user_cannot_submit_event_creation(self):
        request = RequestFactory().post("/eventos/crear/", data={})
        request.user = AnonymousUser()

        response = crear_evento(request)

        self.assertEqual(response.status_code, 302)


class EventoImageStorageConfigTests(SimpleTestCase):
    def test_without_supabase_variables_uses_local_storage(self):
        config = build_event_image_storage_config({})

        self.assertEqual(
            config["BACKEND"],
            "django.core.files.storage.FileSystemStorage",
        )
        self.assertIsInstance(storages.create_storage(config), FileSystemStorage)

    def test_configured_variables_select_private_supabase_storage(self):
        env = {
            "SUPABASE_S3_ENDPOINT_URL": "https://project-ref.storage.supabase.co/storage/v1/s3",
            "SUPABASE_S3_REGION": "us-east-1",
            "SUPABASE_S3_ACCESS_KEY_ID": "test-access-key",
            "SUPABASE_S3_SECRET_ACCESS_KEY": "test-secret-key",
            "SUPABASE_STORAGE_BUCKET": "educatec-media",
        }
        config = build_event_image_storage_config(env)
        storage = storages.create_storage(config)

        self.assertEqual(config["BACKEND"], "storages.backends.s3.S3Storage")
        self.assertIsInstance(storage, S3Storage)
        self.assertEqual(storage.bucket_name, "educatec-media")
        self.assertTrue(storage.querystring_auth)
        self.assertIsNone(storage.default_acl)

    def test_partial_supabase_configuration_fails_closed(self):
        with self.assertRaises(ImproperlyConfigured):
            build_event_image_storage_config({"SUPABASE_S3_ENDPOINT_URL": "https://example.invalid"})

    def test_production_without_supabase_configuration_fails_closed(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "require Supabase Storage"):
            build_event_image_storage_config({"DEBUG": "false"})

    def test_non_debug_environment_without_supabase_fails_closed(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "require Supabase Storage"):
            build_event_image_storage_config({"DEBUG": "release"})

    def test_supabase_endpoint_and_bucket_must_match_project_configuration(self):
        env = {
            "SUPABASE_S3_ENDPOINT_URL": "http://project-ref.storage.supabase.co/storage/v1/s3",
            "SUPABASE_S3_REGION": "us-east-1",
            "SUPABASE_S3_ACCESS_KEY_ID": "test-access-key",
            "SUPABASE_S3_SECRET_ACCESS_KEY": "test-secret-key",
            "SUPABASE_STORAGE_BUCKET": "educatec-media",
        }
        with self.assertRaisesMessage(ImproperlyConfigured, "HTTPS Supabase S3 endpoint"):
            build_event_image_storage_config(env)

        env["SUPABASE_S3_ENDPOINT_URL"] = "https://project-ref.storage.supabase.co/storage/v1/s3"
        env["SUPABASE_STORAGE_BUCKET"] = "another-bucket"
        with self.assertRaisesMessage(ImproperlyConfigured, "educatec-media"):
            build_event_image_storage_config(env)

    def test_configured_storage_generates_signed_urls(self):
        storage = storages.create_storage(
            build_event_image_storage_config(
                {
                    "SUPABASE_S3_ENDPOINT_URL": "https://project-ref.storage.supabase.co/storage/v1/s3",
                    "SUPABASE_S3_REGION": "us-east-1",
                    "SUPABASE_S3_ACCESS_KEY_ID": "test-access-key",
                    "SUPABASE_S3_SECRET_ACCESS_KEY": "test-secret-key",
                    "SUPABASE_STORAGE_BUCKET": "educatec-media",
                }
            )
        )

        query = parse_qs(urlparse(storage.url("eventos/prueba.jpg")).query)
        self.assertIn("X-Amz-Signature", query)

    def test_router_preserves_legacy_paths_and_routes_new_uploads_to_supabase(self):
        local = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
        remote = build_event_image_storage_config(
            {
                "SUPABASE_S3_ENDPOINT_URL": "https://project-ref.storage.supabase.co/storage/v1/s3",
                "SUPABASE_S3_REGION": "us-east-1",
                "SUPABASE_S3_ACCESS_KEY_ID": "test-access-key",
                "SUPABASE_S3_SECRET_ACCESS_KEY": "test-secret-key",
                "SUPABASE_STORAGE_BUCKET": "educatec-media",
            }
        )
        with override_settings(
            STORAGES={"default": {"BACKEND": "apps.eventos.storage.EventoImageStorageRouter"}, "local_media": local, "event_images": remote}
        ):
            router = EventoImageStorageRouter()
            self.assertIsInstance(router._storage_for("eventos/prueba.jpg"), S3Storage)
            self.assertIsInstance(router._storage_for("durable/cursos/curso.jpg"), S3Storage)
            self.assertIsInstance(router._storage_for("durable/imagenes/tarea.jpg"), S3Storage)
            self.assertIsInstance(router._storage_for("durable/archivos/guia.pdf"), S3Storage)
            for path in ("cursos/curso-antiguo.jpg", "imagenes/tarea-antigua.jpg", "archivos/guia-antigua.pdf"):
                with self.subTest(path=path):
                    self.assertIsInstance(router._storage_for(path), FileSystemStorage)

    def test_new_course_uploads_are_saved_under_the_durable_prefix(self):
        router = EventoImageStorageRouter()
        remote_storage = Mock()
        remote_storage.save.return_value = "durable/cursos/curso.jpg"
        content = ContentFile(b"image-bytes", name="curso.jpg")

        with patch.object(router, "_storage_for", return_value=remote_storage) as resolver:
            saved_name = router._save("cursos/curso.jpg", content)

        resolver.assert_called_once_with("durable/cursos/curso.jpg")
        remote_storage.save.assert_called_once_with("durable/cursos/curso.jpg", content)
        self.assertEqual(saved_name, "durable/cursos/curso.jpg")

    def test_router_keeps_unrecognized_media_local(self):
        router = EventoImageStorageRouter()

        self.assertIsInstance(router._storage_for("otros/course.jpg"), FileSystemStorage)
        self.assertIsInstance(router._storage_for("documentos/guia.pdf"), FileSystemStorage)
