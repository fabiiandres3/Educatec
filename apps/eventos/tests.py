from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage, storages
from django.test import SimpleTestCase, override_settings
from storages.backends.s3 import S3Storage

from urllib.parse import urlparse, parse_qs

from apps.eventos.storage import (
    EventoImageStorageRouter,
    build_event_image_storage_config,
)


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

    def test_router_sends_event_images_to_supabase(self):
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
            self.assertIsInstance(router._storage_for("cursos/curso.jpg"), FileSystemStorage)

    def test_router_keeps_non_event_media_local(self):
        router = EventoImageStorageRouter()

        self.assertIsInstance(router._storage_for("cursos/course.jpg"), FileSystemStorage)
        self.assertIsInstance(router._storage_for("imagenes/tarea.jpg"), FileSystemStorage)
