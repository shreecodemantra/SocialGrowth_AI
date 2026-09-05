"""
Object storage (S3 / Cloudflare R2) client used to persist generated
images/videos/thumbnails (section 7). Business logic never stores binary
blobs in PostgreSQL — only the resulting `storage_url` is saved on `assets`.
"""
import uuid

import boto3
from botocore.client import Config as BotoConfig

from app.core.config import settings


class StorageService:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            config=BotoConfig(signature_version="s3v4"),
        )
        self._bucket = settings.S3_BUCKET_NAME

    def _public_url(self, key: str) -> str:
        if settings.S3_PUBLIC_BASE_URL:
            return f"{settings.S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"
        return f"{settings.S3_ENDPOINT_URL}/{self._bucket}/{key}"

    def upload_bytes(self, data: bytes, *, content_type: str, key_prefix: str = "assets") -> str:
        extension = content_type.split("/")[-1] if "/" in content_type else "bin"
        key = f"{key_prefix}/{uuid.uuid4()}.{extension}"
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)
        return self._public_url(key)
