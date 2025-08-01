import boto3
from django.conf import settings

from .base import StorageService


class S3StorageService(StorageService):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.custom_domain = settings.AWS_S3_CUSTOM_DOMAIN

    def upload(self, file_obj, document_id):
        self.s3.upload_fileobj(file_obj, self.bucket, document_id)
        url = f"{self.custom_domain}/{document_id}"
        return {
            "url": url,
            "document_id": document_id,
        }

    def delete(self, document_id):
        self.s3.delete_object(Bucket=self.bucket, Key=document_id)

    def generate_presigned_post_url(self, document_id, content_type, expires_in=3600):
        presigned_post = self.s3.generate_presigned_post(
            Bucket=self.bucket,
            Key=document_id,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 0, 10 * 1024 * 1024],  # 10 mb
            ],
            ExpiresIn=expires_in,
        )

        return {
            "upload_url": presigned_post["url"],
            "fields": presigned_post["fields"],
            "document_id": document_id,
            "file_url": f"{self.custom_domain}/{document_id}",
        }

    def generate_presigned_get_url(
        self, document_id, content_type="application/octet-stream", expires_in=3600
    ):
        """
        Generate a presigned GET URL for accessing the object.

        Args:
            document_id (str): The S3 object key.
            content_type (str): Response content type for the file.
            expires_in (int): Time in seconds for URL expiry.

        Returns:
            dict: Contains the presigned URL and document ID.
        """
        presigned_url = self.s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket,
                "Key": document_id,
                "ResponseContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        return {
            "file_url": presigned_url,
            "document_id": document_id,
        }