import logging

from botocore.exceptions import ClientError
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.filestorage.utils import generate_storage_key

from .models import Files
from .storage.factory import get_storage_service

logger = logging.getLogger(__name__)


def generate_presigned_url(file_name, content_type, folder_prefix="uploads"):
    if not file_name:
        raise ValueError("File name is required field")

    storage_service = get_storage_service()
    document_id = generate_storage_key(file_name, folder_prefix)

    if hasattr(storage_service, "generate_presigned_post_url"):
        return storage_service.generate_presigned_post_url(document_id, content_type)

    return {"upload_url": None, "fields": None, "backend": "local"}


def generate_batch_presigned_urls(files):
    storage_service = get_storage_service()

    if hasattr(storage_service, "generate_presigned_post_url"):
        presigned_list = []

        for index, file_data in enumerate(files):
            file_name = file_data.get("file_name")
            if not file_name:
                raise ValueError(f"Missing 'file_name' in file entry at index {index}")

            content_type = file_data.get("content_type", "application/octet-stream")
            folder_prefix = file_data.get("folder_prefix", "uploads")
            file_id = file_data.get("id") or file_name

            document_id = generate_storage_key(file_name, prefix=folder_prefix)

            presigned = storage_service.generate_presigned_post_url(
                document_id, content_type
            )
            presigned["input_file_id"] = file_id
            presigned_list.append(presigned)

        return {"backend": "s3", "presigned": presigned_list}

    return {"backend": "local", "presigned": []}


def save_file_metadata(
    user, file_url, original_name, content_type_str, object_id, document_type
):
    app_label, model = content_type_str.split(".")
    content_type = ContentType.objects.get(app_label=app_label, model=model)

    uploaded_file = Files.objects.create(
        file=file_url,
        original_name=original_name,
        uploaded_by=user,
        content_type=content_type,
        object_id=object_id,
        document_type=document_type,
    )
    return uploaded_file


def delete_file_from_s3(key: str, user=None) -> None:
    """
    Delete a file from the S3 bucket and its metadata from the Files table.

    Args:
        key (str): The S3 object key of the file to delete (e.g., 'uploads/example.jpg').
        user (User, optional): The user requesting the deletion, used for permission checks.

    Raises:
        ValidationError: If the key is empty or the user lacks permission.
        Exception: If the deletion from S3 or database fails.
    """
    if not key:
        raise ValidationError("File key is required for deletion.")

    try:
        with transaction.atomic():
            file_upload = Files.objects.filter(file=key).first()
            if not file_upload:
                logger.warning(f"No metadata found for key: {key}")
            elif user and file_upload.uploaded_by != user:
                raise ValidationError("You do not have permission to delete this file.")

            # Delete from S3
            storage_service = get_storage_service()
            if hasattr(storage_service, "delete_object"):
                storage_service.delete(document_id=key)
                logger.info(f"Successfully deleted file from S3: {key}")
            else:
                logger.warning(f"Storage service does not support deletion: {key}")

            # Delete metadata from Files table
            deleted_count, _ = Files.objects.filter(id=key).delete()
            if deleted_count > 0:
                logger.info(f"Successfully deleted metadata for key: {key}")
            else:
                logger.warning(f"No metadata found for key: {key}")

    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {key}, Error: {str(e)}")
        raise Exception(f"Failed to delete file from S3: {str(e)}")
    except ValidationError as e:
        logger.error(f"Validation error during deletion: {key}, Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to delete file metadata: {key}, Error: {str(e)}")
        raise Exception(f"Failed to delete file metadata: {str(e)}")

def generate_presigned_get_url(
    file_url, content_type="application/octet-stream", expires_in=3600
):
    """
    Generate a presigned GET URL for accessing the S3 object.

    Args:
        file_url (str): The full S3 URL or S3 key (e.g., 'uploads/example.jpg').
        content_type (str): (Optional) The content type to return.
        expires_in (int): (Optional) Expiry time in seconds (default: 1 hour).

    Returns:
        dict: {'file_url': presigned_url, 'document_id': s3_key}
    """
    if not file_url:
        raise ValueError("file_url is required.")

    storage_service = get_storage_service()

    s3_key = file_url
    if "amazonaws.com/" in file_url or ".com/" in file_url:
        s3_key = file_url.split(".com/")[-1]

    if hasattr(storage_service, "generate_presigned_get_url"):
        return storage_service.generate_presigned_get_url(
            document_id=s3_key, content_type=content_type, expires_in=expires_in
        )
    else:
        raise NotImplementedError(
            "The storage backend does not support presigned GET URLs."
        )
