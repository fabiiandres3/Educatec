import logging
from uuid import uuid4
from urllib.parse import parse_qs, urlsplit

from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Prueba subida, lectura, URL firmada y borrado en Supabase Storage para eventos."

    def handle(self, *args, **options):
        storage = storages["default"]
        object_name = f"eventos/_diagnostico/{uuid4().hex}.txt"
        payload = b"Educatec Supabase Storage diagnostic"
        saved_name = None
        failure = None

        try:
            saved_name = storage.save(object_name, ContentFile(payload))
            if not storage.exists(saved_name):
                raise RuntimeError("El objeto no aparece despues de subirlo.")

            with storage.open(saved_name, "rb") as stored_file:
                if stored_file.read() != payload:
                    raise RuntimeError("El contenido descargado no coincide.")

            signed_url = storage.url(saved_name)
            parsed_url = urlsplit(signed_url)
            if parsed_url.scheme != "https" or not parsed_url.netloc:
                raise RuntimeError("El almacenamiento genero una URL no HTTPS valida.")
            if "X-Amz-Signature" not in parse_qs(parsed_url.query):
                raise RuntimeError("El almacenamiento no genero la firma S3 esperada.")

        except Exception as exc:
            failure = exc
            logger.exception("Supabase event storage diagnostic failed (object=%s)", object_name)

        cleanup_failed = False
        if saved_name:
            try:
                storage.delete(saved_name)
                if storage.exists(saved_name):
                    raise RuntimeError("El objeto de diagnostico sigue presente despues del borrado.")
            except Exception as exc:
                cleanup_failed = True
                logger.exception("Could not remove diagnostic storage object (object=%s)", saved_name)

        if failure:
            raise CommandError(
                f"Fallo la prueba de almacenamiento ({type(failure).__name__}). "
                "Consulta los logs y verifica las variables SUPABASE_* en Render."
            ) from failure
        if cleanup_failed:
            raise CommandError(
                "La subida y lectura funcionaron, pero no se pudo borrar el objeto de prueba. "
                "Revisa los logs y elimina el archivo de eventos/_diagnostico/ en Supabase."
            )

        self.stdout.write(self.style.SUCCESS(
            "OK: subida, lectura, generación de URL y borrado verificados; "
            f"host de URL: {parsed_url.netloc}."
        ))
