import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any

class CertificateService:
    @staticmethod
    def generate_qr_code(document_hash: str, verification_id: str, base_verify_url: str = "http://localhost:3000/verify") -> str:
        """
        Generates QR code targeting public verification portal URL.
        """
        target_url = f"{base_verify_url}/{document_hash}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(target_url)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
        
        from app.utils.paths import CERT_DIR
        qr_path = os.path.join(str(CERT_DIR), f"qr_{verification_id}.png")
        qr_img.save(qr_path)
        
        return f"/static/certificates/qr_{verification_id}.png"

    @staticmethod
    def generate_certificate_data(
        verification_id: str,
        survey_number: str,
        district: str,
        taluk: str,
        village: str,
        area_sqft: float,
        document_hash: str,
        tx_hash: str,
        status: str,
        qr_url: str
    ) -> Dict[str, Any]:
        """
        Builds digital verification certificate payload.
        """
        return {
            "title": "DIGITAL LAND VERIFICATION CERTIFICATE",
            "issuer": "GOVERNMENT REGISTRY & PLOTPROOF AUDIT NETWORK",
            "verification_id": verification_id,
            "survey_number": survey_number,
            "district": district,
            "taluk": taluk,
            "village": village,
            "area_sqft": area_sqft,
            "area_sqm": round(area_sqft * 0.092903, 2),
            "status": status,
            "spatial_validation": "PASSED (0 COLLISIONS)" if status == "VERIFIED" else "FAILED",
            "document_integrity": "CRYPTOGRAPHICALLY TAMPER-EVIDENT",
            "blockchain_status": "REGISTERED (ON-CHAIN)",
            "document_fingerprint": document_hash,
            "transaction_hash": tx_hash,
            "qr_code_url": qr_url,
            "public_verify_link": f"/verify/{document_hash}"
        }
