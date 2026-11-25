import logging
from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage, storages

logger = logging.getLogger(__name__)
EVENT_IMAGE_BUCKET = "educatec-media"

SUPABASE_CONNECTION_VARIABLES = (
    "SUPABASE_S3_ENDPOINT_URL",
    "SUPABASE_S3_REGION",
    "SUPABASE_S3_ACCESS_KEY_ID",
    "SUPABASE_S3_SECRET_ACCESS_KEY",
)


def build_event_image_storage_config(env):
    """Use local storage only for development; events are durable in production."""
    configured = any(env.get(name) for name in SUPABASE_CONNECTION_VARIABLES)
    if not configured:
        is_production = bool(env.get("RENDER_EXTERNAL_HOSTNAME")) or env.get(
            "DEBUG", "true"
        ).lower() in {"0", "false", "no"}
        if is_production:
            raise ImproperlyConfigured(
                "Event images require Supabase Storage in production. Configure "
                + ", ".join(SUPABASE_CONNECTION_VARIABLES)
                + " in the deployment environment."
            )
        logger.warning("Supabase Storage is not configured; event images use local development storage.")
        return {"BACKEND": "django.core.files.storage.FileSystemStorage"}

    missing = [name for name in SUPABASE_CONNECTION_VARIABLES if not env.get(name)]
    if missing:
        raise ImproperlyConfigured(
            "Supabase Storage configuration is incomplete; set: " + ", ".join(missing)
        )

    endpoint = env["SUPABASE_S3_ENDPOINT_URL"].strip().rstrip("/")
    endpoint_parts = urlparse(endpoint)
    if (
        endpoint_parts.scheme != "https"
        or not endpoint_parts.netloc
        or not endpoint_parts.hostname
        or not endpoint_parts.hostname.endswith(".supabase.co")
        or not endpoint_parts.path.rstrip("/").endswith("/storage/v1/s3")
        or endpoint_parts.query
        or endpoint_parts.fragment
    ):
        raise ImproperlyConfigured(
            "SUPABASE_S3_ENDPOINT_URL must be the HTTPS Supabase S3 endpoint "
            "ending in /storage/v1/s3."
        )
    bucket_name = env.get("SUPABASE_STORAGE_BUCKET", EVENT_IMAGE_BUCKET).strip()
    if bucket_name != EVENT_IMAGE_BUCKET:
        raise ImproperlyConfigured(
            f"SUPABASE_STORAGE_BUCKET must be exactly '{EVENT_IMAGE_BUCKET}'."
        )

    return {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": bucket_name,
            "endpoint_url": endpoint,
            "region_name": env["SUPABASE_S3_REGION"],
            "access_key": env["SUPABASE_S3_ACCESS_KEY_ID"],
            "secret_key": env["SUPABASE_S3_SECRET_ACCESS_KEY"],
            "addressing_style": "path",
            "signature_version": "s3v4",
            "querystring_auth": True,
            "default_acl": None,
            "file_overwrite": False,
        },
    }


class EventoImageStorageRouter(Storage):
    """Use Supabase only for Evento's eventos/ upload path."""

    def _storage_for(self, name):
        normalized = str(name).replace("\\", "/").lstrip("/")
        alias = "event_images" if normalized.startswith("eventos/") else "local_media"
        return storages[alias]

    def _open(self, name, mode="rb"):
        return self._storage_for(name).open(name, mode)

    def _save(self, name, content):
        try:
            return self._storage_for(name).save(name, content)
        except Exception:
            logger.exception("Failed to upload media object to configured storage: %s", name)
            raise

    def delete(self, name):
        return self._storage_for(name).delete(name)

    def exists(self, name):
        return self._storage_for(name).exists(name)

    def listdir(self, path):
        normalized = str(path).replace("\\", "/").lstrip("/")
        alias = "event_images" if normalized == "eventos" or normalized.startswith("eventos/") else "local_media"
        return storages[alias].listdir(path)

    def size(self, name):
        return self._storage_for(name).size(name)

    def url(self, name):
        return self._storage_for(name).url(name)

    def path(self, name):
        return self._storage_for(name).path(name)

    def get_accessed_time(self, name):
        return self._storage_for(name).get_accessed_time(name)

    def get_created_time(self, name):
        return self._storage_for(name).get_created_time(name)

    def get_modified_time(self, name):
        return self._storage_for(name).get_modified_time(name)
