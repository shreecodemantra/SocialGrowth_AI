"""
Object storage (S3 / Cloudflare R2) client used to persist generated
images/videos/thumbnails (section 7). Business logic never stores binary
blobs in PostgreSQL — only the resulting `storage_url` is saved on `assets`.

`get_storage_service()` is what the rest of the app should call: it returns
the real S3/R2-backed client when credentials are configured, and a
filesystem-backed fallback otherwise, so the content pipeline runs
end-to-end locally/in tests/in CI without needing real cloud credentials.
"""
import uuid
from pathlib import Path
from typing import Protocol

import boto3
from botocore.client import Config as BotoConfig

from app.core.config import settings


class ObjectStorage(Protocol):
    def upload_bytes(self, data: bytes, *, content_type: str, key_prefix: str = "assets") -> str: ...


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


class LocalStorageService:
    """
    Filesystem-backed fallback used when S3/R2 credentials aren't configured
    (local development, CI, tests). Writes under `backend/media/` and serves
    it via the `/media` static mount registered in `app/main.py`. Switch to
    real object storage in production by setting S3_ENDPOINT_URL /
    S3_ACCESS_KEY_ID / S3_SECRET_ACCESS_KEY in `.env`.
    """

    def __init__(self, base_dir: Path | None = None):
        self._base_dir = base_dir or (Path(__file__).resolve().parents[2] / "media")
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def upload_bytes(self, data: bytes, *, content_type: str, key_prefix: str = "assets") -> str:
        extension = content_type.split("/")[-1] if "/" in content_type else "bin"
        key = f"{key_prefix}/{uuid.uuid4()}.{extension}"
        path = self._base_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"/media/{key}"


def get_storage_service() -> ObjectStorage:
    if settings.S3_ENDPOINT_URL and settings.S3_ACCESS_KEY_ID and settings.S3_SECRET_ACCESS_KEY:
        return StorageService()
    return LocalStorageService()
