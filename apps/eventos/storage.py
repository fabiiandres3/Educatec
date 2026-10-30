from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage, storages


SUPABASE_CONNECTION_VARIABLES = (
    "SUPABASE_S3_ENDPOINT_URL",
    "SUPABASE_S3_REGION",
    "SUPABASE_S3_ACCESS_KEY_ID",
    "SUPABASE_S3_SECRET_ACCESS_KEY",
    "SUPABASE_STORAGE_BUCKET",
)


def build_event_image_storage_config(env):
    """Return a local fallback or a private Supabase S3 storage config."""
    configured = any(env.get(name) for name in SUPABASE_CONNECTION_VARIABLES)
    if not configured:
        return {"BACKEND": "django.core.files.storage.FileSystemStorage"}

    missing = [name for name in SUPABASE_CONNECTION_VARIABLES if not env.get(name)]
    if missing:
        raise ImproperlyConfigured(
            "Supabase Storage configuration is incomplete; set: " + ", ".join(missing)
        )

    return {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": env["SUPABASE_STORAGE_BUCKET"],
            "endpoint_url": env["SUPABASE_S3_ENDPOINT_URL"],
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
        return self._storage_for(name).save(name, content)

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
