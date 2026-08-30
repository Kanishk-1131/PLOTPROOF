import hashlib
import os


def sha256_bytes(data: bytes) -> str:
    """
    Computes a deterministic SHA-256 hexadecimal digest for arbitrary byte streams (Section 4).
    """
    return hashlib.sha256(data).hexdigest()


def sha256_file(file_path: str, chunk_size: int = 65536) -> str:
    """
    Computes SHA-256 hash for a file stream efficiently using chunked streaming.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
