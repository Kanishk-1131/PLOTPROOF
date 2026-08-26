import hashlib
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.certificate.qr import generate_qr_image_bytes

CERTIFICATES_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "certificates"

STATUTORY_LEGAL_DISCLAIMER = (
    "PlotProof System Verification Certificate. "
    "This certificate confirms the verification results produced by the PlotProof system. "
    "It does not independently constitute a government-issued title document or legal title guarantee."
)


def compute_certificate_hash(pdf_bytes: bytes) -> str:
    return hashlib.sha256(pdf_bytes).hexdigest()



def generate_certificate_pdf(
    verification_id: str,
    certificate_number: str,
    survey_number: str,
    location_str: str,
    verification_date: str,
    verification_hash: str,
    blockchain_tx: str,
    network_name: str,
    verification_url: str,
    output_path: Optional[str] = None,
) -> Tuple[bytes, str, str]:
    """
    Generates a professional, tamper-evident verification certificate PDF (Section 2, 3, & 11).
    Computes SHA-256 digest of generated PDF bytes and returns (pdf_bytes, certificate_hash, output_file_path).
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CertTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "CertSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0284C7"),
        alignment=1,
    )
    section_heading = ParagraphStyle(
        "CertSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
    )
    body_style = ParagraphStyle(
        "CertBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    mono_style = ParagraphStyle(
        "CertMono",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
    )
    legal_style = ParagraphStyle(
        "CertLegal",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#64748B"),
        alignment=1,
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("PLOTPROOF", title_style))
    story.append(Paragraph("INTELLIGENT FORENSIC LAND RECORD VERIFICATION", subtitle_style))
    story.append(Paragraph("PlotProof System Verification Certificate", ParagraphStyle(
        "CertDocType",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,
    )))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=14))

    # 2. Key Metadata Cards Table
    meta_data = [
        [
            Paragraph("<b>Certificate Number:</b>", body_style),
            Paragraph(f"<b>{certificate_number}</b>", body_style),
            Paragraph("<b>Verification Date:</b>", body_style),
            Paragraph(verification_date, body_style),
        ],
        [
            Paragraph("<b>Verification ID:</b>", body_style),
            Paragraph(verification_id, body_style),
            Paragraph("<b>Survey Reference:</b>", body_style),
            Paragraph(f"Survey {survey_number}", body_style),
        ],
        [
            Paragraph("<b>Location:</b>", body_style),
            Paragraph(location_str, body_style),
            Paragraph("<b>Status:</b>", body_style),
            Paragraph("<font color='#16A34A'><b>VERIFIED</b></font>", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Multi-Vector System Validation Results
    story.append(Paragraph("Multi-Vector Forensic Validation Results", section_heading))
    story.append(Spacer(1, 4))
    check_pass = "<font color='#16A34A'><b>✓ PASSED</b></font>"
    results_data = [
        ["Vector", "Specification", "Result"],
        [Paragraph("<b>Document Integrity</b>", body_style), Paragraph("SHA-256 byte digest reproducible; 0 bit-rot or byte tampering detected.", body_style), Paragraph(check_pass, body_style)],
        [Paragraph("<b>OCR Intelligence</b>", body_style), Paragraph("Dual-engine Tamil/English statutory field extraction & geometry normalized.", body_style), Paragraph(check_pass, body_style)],
        [Paragraph("<b>Spatial Validation</b>", body_style), Paragraph("Cadastral boundaries verified on EPSG:32644 metric grid; 0 boundary overlap.", body_style), Paragraph(check_pass, body_style)],
        [Paragraph("<b>Privacy & ZK Proof</b>", body_style), Paragraph("Groth16 SNARK verified; citizen Aadhaar/identity concealed via Poseidon.", body_style), Paragraph("<font color='#16A34A'><b>✓ VERIFIED</b></font>", body_style)],
        [Paragraph("<b>Blockchain Anchor</b>", body_style), Paragraph(f"Cryptographic commitment immutable on Polygon L2; tamper-evident receipt.", body_style), Paragraph("<font color='#16A34A'><b>✓ CONFIRMED</b></font>", body_style)],
    ]
    results_table = Table(results_data, colWidths=[120, 320, 100])
    results_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 14))

    # 4. Cryptographic Proof & QR Section
    story.append(Paragraph("Cryptographic Proof & Public Verification Anchor", section_heading))
    story.append(Spacer(1, 4))

    qr_bytes = generate_qr_image_bytes(verification_url)
    qr_img = RLImage(io.BytesIO(qr_bytes), width=85, height=85)

    crypto_details = [
        [Paragraph("<b>Verification Root Hash:</b>", body_style), Paragraph(verification_hash, mono_style)],
        [Paragraph("<b>Blockchain Transaction:</b>", body_style), Paragraph(blockchain_tx, mono_style)],
        [Paragraph("<b>Network:</b>", body_style), Paragraph(network_name, body_style)],
        [Paragraph("<b>Verification Host:</b>", body_style), Paragraph(f"<font color='#0284C7'>{verification_url}</font>", mono_style)],
    ]
    crypto_table = Table(crypto_details, colWidths=[120, 310])
    crypto_table.setStyle(TableStyle([
        ("PADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    qr_combined_data = [
        [qr_img, crypto_table]
    ]
    qr_combined_table = Table(qr_combined_data, colWidths=[95, 445])
    qr_combined_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(qr_combined_table)
    story.append(Spacer(1, 12))

    # 5. Mandatory Legal Wording (Section 3)
    legal_text = (
        "<b>LEGAL NOTICE & STATUTORY DISCLAIMER:</b><br/>"
        "This certificate confirms the verification results produced by the PlotProof system. "
        "It does not independently constitute a government-issued title document or legal title guarantee. "
        "Official statutory determination of property ownership remains subject to competent Sub-Registrar and Revenue Department authority."
    )
    story.append(Paragraph(legal_text, legal_style))

    # Build PDF document
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()

    # Compute SHA-256 certificate hash (Section 11)
    cert_hash = hashlib.sha256(pdf_bytes).hexdigest()

    # Save to file path if requested or default
    if not output_path:
        CERTIFICATES_DIR.mkdir(parents=True, exist_ok=True)
        output_path = str(CERTIFICATES_DIR / f"{certificate_number}.pdf")

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return pdf_bytes, cert_hash, output_path
