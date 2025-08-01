import os

from django.conf import settings
from django.core.files.storage import default_storage

from .base import StorageService


class LocalStorageService(StorageService):
    def upload(self, file_obj, document_id):
        # Prefix document_id with 'uploads/' to store in media/uploads/
        prefixed_key = os.path.join("uploads", document_id)
        path = os.path.join(settings.MEDIA_ROOT, prefixed_key)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with default_storage.open(prefixed_key, "wb+") as destination:
            if hasattr(file_obj, "chunks"):
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            else:
                destination.write(file_obj.read())

        scheme = "https" if getattr(settings, "USE_HTTPS", False) else "http"
        domain = getattr(settings, "DOMAIN", "localhost:8000")
        url_path = f"{settings.MEDIA_URL}{prefixed_key}"

        return {
            "url": f"{scheme}://{domain}{url_path}",
            "document_id": document_id,
        }

    def delete(self, document_id):
        prefixed_key = os.path.join("uploads", document_id)
        path = os.path.join(settings.MEDIA_ROOT, prefixed_key)
        if os.path.exists(path):
            os.remove(path)
