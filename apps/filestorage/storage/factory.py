from django.conf import settings

from apps.file_upload.storage.local import LocalStorageService
from apps.file_upload.storage.s3 import S3StorageService


def get_storage_service():
    storage_backend = getattr(settings, "STORAGE_BACKEND", "local")
    if storage_backend == "s3":
        return S3StorageService()
    return LocalStorageService()
