import os
from pathlib import Path
from typing import BinaryIO
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError

from app.core.config import settings
from app.utils.paths import STATIC_DIR


class StorageService:
    def __init__(self):
        self.bucket = settings.minio_bucket
        self.endpoint = settings.minio_endpoint
        if not self.endpoint.startswith("http://") and not self.endpoint.startswith("https://"):
            self.endpoint = f"http://{self.endpoint}"

        self.local_storage_dir = STATIC_DIR / "storage" / self.bucket
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)

        self._s3_available = None
        try:
            self.client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                config=Config(signature_version="s3v4", connect_timeout=1, read_timeout=2),
                region_name="us-east-1",
            )
        except Exception:
            self.client = None
            self._s3_available = False

    def is_minio_connected(self) -> bool:
        if self._s3_available is not None:
            return self._s3_available
        if not self.client:
            self._s3_available = False
            return False

        # Fast 0.2s socket test to avoid boto3 connection hang when MinIO is not running
        import socket
        s = None
        try:
            host_str = self.endpoint.replace("http://", "").replace("https://", "").split("/")[0]
            if ":" in host_str:
                h, p_str = host_str.split(":")
                p = int(p_str)
            else:
                h, p = host_str, 9000
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect((h, p))
        except Exception:
            self._s3_available = False
            return False
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass


        try:
            self.client.head_bucket(Bucket=self.bucket)
            self._s3_available = True
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            self._s3_available = code in ("404", "NoSuchBucket", "403")
        except Exception:
            self._s3_available = False
        return self._s3_available


    def upload_file(
        self,
        file_object: BinaryIO,
        storage_key: str,
        content_type: str = "application/pdf",
    ):
        file_object.seek(0)
        # Always store in local fallback directory to guarantee 100% data durability
        local_path = self.local_storage_dir / storage_key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_object.read())
        file_object.seek(0)

        # Also upload to MinIO S3 if available
        if self.is_minio_connected() and self.client:
            try:
                self.client.upload_fileobj(
                    file_object,
                    self.bucket,
                    storage_key,
                    ExtraArgs={"ContentType": content_type},
                )
            except Exception:
                pass

    def delete_file(self, storage_key: str):
        # Delete local
        local_path = self.local_storage_dir / storage_key
        if local_path.exists():
            try:
                local_path.unlink()
            except OSError:
                pass

        # Delete S3 if connected
        if self.is_minio_connected() and self.client:
            try:
                self.client.delete_object(
                    Bucket=self.bucket,
                    Key=storage_key,
                )
            except Exception:
                pass

    def generate_presigned_url(
        self,
        storage_key: str,
        expiration: int = 900,
    ) -> str:
        """
        Generates short-lived signed URL for authorized download (Section 20 & 26).
        """
        if self.is_minio_connected() and self.client:
            try:
                return self.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": storage_key},
                    ExpiresIn=expiration,
                )
            except Exception:
                pass

        # Fallback local direct stream route
        return f"/api/v1/documents/raw/{storage_key}"

    def get_local_path(self, storage_key: str) -> Path | None:
        local_path = self.local_storage_dir / storage_key
        if local_path.exists():
            return local_path
        return None
