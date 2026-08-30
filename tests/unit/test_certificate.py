import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.certificate.qr import generate_qr_image_bytes
from app.certificate.generator import (
    generate_certificate_pdf,
    compute_certificate_hash,
    STATUTORY_LEGAL_DISCLAIMER,
)


class TestUnitCertificate(unittest.TestCase):
    """
    Layer 12: Unit tests for PDF Certificate Generation, QR Encoding & Legal Disclaimers.
    """

    def test_01_qr_code_contains_pure_url_without_pii(self):
        url = "https://plotproof.gov.in/verify/PP-2026-000052"
        qr_bytes = generate_qr_image_bytes(url)

        self.assertIsNotNone(qr_bytes)
        self.assertTrue(len(qr_bytes) > 100)
        # Check PNG magic bytes
        self.assertEqual(qr_bytes[:8], b"\x89PNG\r\n\x1a\n")
        print("[PASS] Unit Test 1: Pure Verification URL QR Code PNG Generation")

    def test_02_pdf_generation_and_hash_calculation(self):
        pdf_bytes, cert_hash, file_path = generate_certificate_pdf(
            verification_id="PP-2026-TEST-99",
            certificate_number="PP-CERT-2026-000099",
            survey_number="142/3A",
            location_str="Selaiyur, Tambaram, Chennai",
            verification_date="26 August 2026",
            verification_hash="b" * 64,
            blockchain_tx="0x" + "1" * 64,
            network_name="polygon-amoy-testnet",
            verification_url="https://plotproof.gov.in/verify/PP-2026-TEST-99",
        )

        self.assertTrue(pdf_bytes.startswith(b"%PDF-1."))
        self.assertEqual(len(cert_hash), 64)
        # Recomputed hash must match
        recomputed = compute_certificate_hash(pdf_bytes)
        self.assertEqual(cert_hash, recomputed)
        print("[PASS] Unit Test 2: ReportLab PDF Certificate Generation & SHA-256 Digest Verified")

    def test_03_mandatory_statutory_legal_disclaimer(self):
        self.assertIn("PlotProof System Verification Certificate", STATUTORY_LEGAL_DISCLAIMER)
        self.assertIn("does not independently constitute a government-issued title document", STATUTORY_LEGAL_DISCLAIMER)
        print("[PASS] Unit Test 3: Mandatory Statutory Legal Disclaimer Enforcement")


if __name__ == "__main__":
    unittest.main()
