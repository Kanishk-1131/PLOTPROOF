from botocore.exceptions import ClientError
from app.services.storage_service import StorageService


def ensure_bucket_exists():
    storage = StorageService()
    if not storage.client or not storage.is_minio_connected():
        return

    try:
        storage.client.head_bucket(Bucket=storage.bucket)
    except ClientError:
        try:
            storage.client.create_bucket(Bucket=storage.bucket)
        except Exception:
            pass
    except Exception:
        pass
