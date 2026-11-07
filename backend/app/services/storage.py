"""
SIP Intelligence — MinIO / S3-compatible Object Storage Service
"""
from __future__ import annotations

import io
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class StorageService:
    """Abstraction layer over MinIO / S3-compatible object storage."""

    def __init__(self):
        self._client: Optional[Minio] = None

    @property
    def client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_use_ssl,
            )
        return self._client

    async def ensure_buckets(self):
        """Create default buckets if they don't exist."""
        buckets = [
            settings.minio_bucket_documents,
            settings.minio_bucket_processed,
            settings.minio_bucket_symbols,
            settings.minio_bucket_exports,
        ]
        try:
            for bucket in buckets:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
        except Exception:
            from pathlib import Path
            for bucket in buckets:
                (Path("d:/newsas/data/storage") / bucket).mkdir(parents=True, exist_ok=True)

    async def upload_bytes(
        self,
        bucket: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload bytes to object storage or local filesystem."""
        try:
            self.client.put_object(
                bucket,
                object_name,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            return f"{bucket}/{object_name}"
        except Exception:
            from pathlib import Path
            target = Path("d:/newsas/data/storage") / bucket / object_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            return f"{bucket}/{object_name}"

    async def download_bytes(self, bucket: str, object_name: str) -> bytes:
        """Download an object as bytes."""
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete_object(self, bucket: str, object_name: str):
        """Delete an object."""
        self.client.remove_object(bucket, object_name)

    def generate_presigned_url(
        self, bucket: str, object_name: str, expires_hours: int = 1
    ) -> str:
        """Generate a presigned URL for temporary access."""
        from datetime import timedelta
        return self.client.presigned_get_object(
            bucket, object_name, expires=timedelta(hours=expires_hours)
        )


storage_service = StorageService()

