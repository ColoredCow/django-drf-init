from django.conf import settings

from apps.filestorage.storage.local import LocalStorageService
from apps.filestorage.storage.s3 import S3StorageService


def get_storage_service():
    storage_backend = getattr(settings, "STORAGE_BACKEND", "local")
    if storage_backend == "s3":
        return S3StorageService()
    return LocalStorageService()
