import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.common.responses import error_response, success_response

from .serializers import FileSerializer
from .services import (
    delete_file_from_s3,
    generate_batch_presigned_urls,
    generate_presigned_url,
    save_file_metadata,
)

logger = logging.getLogger(__name__)


class FileUploadViewSet(viewsets.ViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @action(methods=["post"], detail=False, url_path="generate-presigned-url")
    def generate_presigned_url_view(self, request):
        file_name = request.data.get("file_name")
        content_type = request.data.get("content_type", "application/octet-stream")
        folder_prefix = request.data.get("folder_prefix", "uploads")
        try:
            result = generate_presigned_url(file_name, content_type, folder_prefix)
            return success_response(
                data=result,
                message="Presigned URL generated successfully",
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return error_response(
                message="Validation failed",
                error={"code": "PRESIGNED_URL_GENERATION_FAILED", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(f"Failed to generate presigned URL: {e}")
            return error_response(
                message="Failed to generate presigned URL",
                error={"code": "PRESIGNED_URL_GENERATION_FAILED", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["post"], detail=False, url_path="save-file-metadata")
    def save_file_metadata(self, request):
        data = request.data

        try:
            uploaded_file = save_file_metadata(
                user=request.user,
                file_url=data["file_url"],
                original_name=data["original_name"],
                content_type_str=data["content_type"],
                object_id=data["object_id"],
                document_type=data.get("document_type", ""),
            )
            result = FileSerializer(uploaded_file).data
        except Exception as e:
            logger.exception(f"Failed to save file metadata: {e}")
            return error_response(
                message="Failed to save file metadata",
                error={"code": "FAILED_TO_SAVE_METADATA", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return success_response(
            data=result,
            message="File Meta stored successfully",
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["post"], detail=False, url_path="generate-batch-presigned-urls")
    def generate_batch_presigned_urls_view(self, request):
        files = request.data.get("files", [])
        if not files or not isinstance(files, list):
            return error_response(
                message="File data not found in the request",
                error={
                    "code": "DATA_NOT_AVAILABLE",
                    "details": "File details are not available in the request",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = generate_batch_presigned_urls(files)
            return success_response(
                data=result,
                message="Presigned URLs generated successfully",
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return error_response(
                message="Validation failed",
                error={"code": "PRESIGNED_URL_GENERATION_FAILED", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(f"Failed to generate presigned URLs: {e}")
            return error_response(
                message="Failed to generate presigned URLs",
                error={"code": "PRESIGNED_URL_GENERATION_FAILED", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["post"], detail=False, url_path="delete-file")
    def delete_file(self, request):
        key = request.data.get("key")
        if not key:
            return error_response(
                message="File key is required",
                error={
                    "code": "INVALID_REQUEST",
                    "details": "The 'key' field is missing in the request data",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            delete_file_from_s3(key, user=request.user)
            return success_response(
                data={},
                message="File deleted successfully from S3 and database",
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return error_response(
                message="Validation failed",
                error={"code": "DELETE_FILE_FAILED", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception(f"Failed to delete file: {e}")
            return error_response(
                message="Failed to delete file",
                error={"code": "DELETE_FILE_FAILED", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
