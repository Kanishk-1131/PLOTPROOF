import io
from pathlib import Path
from typing import Optional
import qrcode
from qrcode.image.pil import PilImage


def generate_qr_image_bytes(verification_url: str) -> bytes:
    """
    Generates PNG bytes of a QR code encoding ONLY the public verification URL (Section 7 & 8).
    Strictly omits citizen PII, raw deeds, or private keys.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save_qr_code(verification_url: str, output_path: str) -> str:
    """
    Saves QR code image to a target file path.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img_bytes = generate_qr_image_bytes(verification_url)
    with open(output_path, "wb") as f:
        f.write(img_bytes)
    return output_path
