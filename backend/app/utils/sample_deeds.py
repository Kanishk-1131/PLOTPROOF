import os
import sys
import hashlib
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from app.utils.paths import UPLOAD_DIR, STATIC_DIR

SAMPLE_DEEDS_INFO = {
    "default": {
        "title": "GOVERNMENT OF TAMIL NADU - TITLE DEED OF SALE",
        "doc_number": "4821/2024",
        "book": "Book 1, Volume 912, Pages 101 to 114",
        "sro": "Sub-Registrar Office: Tambaram",
        "district": "Chennai",
        "taluk": "Tambaram",
        "village": "Selaiyur Village",
        "survey_number": "142/3A",
        "area_sqft": "2,400 Sq.ft (equivalent to 222.96 Sq.meters / 5.5 Cents)",
        "boundaries": {
            "north": "Survey No 142/2 (Road 30ft width)",
            "south": "Survey No 142/4 (Vacant Plot)",
            "east": "Survey No 142/3B (Adjacent Plot)",
            "west": "Survey No 142/1 (Residential Property)"
        },
        "gps": "12.9249 N, 80.1472 E to 12.9255 N, 80.1478 E",
        "purchaser": "K. S. Ramanathan",
        "father_name": "Late K. Sundaram",
        "aadhaar_masked": "5412-8823-8912",
        "registered_hash": "7c3e8f2c9a620d41e7845f096231ba4190284e91240185e2b028941785e091ad",
        "filename_txt": "sample_genuine_142_3A.txt",
        "filename_pdf": "sample_default_deed.pdf"
    },
    "tampered": {
        "title": "GOVERNMENT OF TAMIL NADU - TITLE DEED OF SALE",
        "doc_number": "4821/2024",
        "book": "Book 1, Volume 912, Pages 101 to 114",
        "sro": "Sub-Registrar Office: Tambaram",
        "district": "Chennai",
        "taluk": "Tambaram",
        "village": "Selaiyur Village",
        "survey_number": "142/3A",
        "area_sqft": "3,400 Sq.ft (equivalent to 315.87 Sq.meters) [ALTERED]",
        "boundaries": {
            "north": "Survey No 142/2 (Road 30ft width)",
            "south": "Survey No 142/4 (Vacant Plot)",
            "east": "Survey No 142/3B (Adjacent Plot)",
            "west": "Survey No 142/1 (Residential Property)"
        },
        "gps": "12.9249 N, 80.1472 E to 12.9255 N, 80.1478 E",
        "purchaser": "K. S. Ramanathan",
        "father_name": "Late K. Sundaram",
        "aadhaar_masked": "5412-8823-8912",
        "registered_hash": "7c3e8f2c9a620d41e7845f096231ba4190284e91240185e2b028941785e091ad",
        "filename_txt": "sample_tampered_area.txt",
        "filename_pdf": "demo_tampered_deed.pdf"
    },
    "collision": {
        "title": "GOVERNMENT OF TAMIL NADU - TITLE DEED OF SALE",
        "doc_number": "5109/2024",
        "book": "Book 1, Volume 915, Pages 45 to 58",
        "sro": "Sub-Registrar Office: Tambaram",
        "district": "Chennai",
        "taluk": "Tambaram",
        "village": "Selaiyur Village",
        "survey_number": "142/3B",
        "area_sqft": "2,400 Sq.ft (equivalent to 222.96 Sq.meters)",
        "boundaries": {
            "north": "Survey No 142/2",
            "south": "Survey No 142/4",
            "east": "Survey No 142/5",
            "west": "Survey No 142/3A"
        },
        "gps": "12.9252 N, 80.1476 E to 12.9258 N, 80.1482 E (Overlaps 142/3A)",
        "purchaser": "M. Vijay Anand",
        "father_name": "R. Mohan",
        "aadhaar_masked": "8721-3312-9014",
        "registered_hash": "3b1d7e8a9f33...cadastral-collision",
        "filename_txt": "sample_collision_142_3B.txt",
        "filename_pdf": "demo_collision_deed.pdf"
    }
}


def generate_sample_pdf_deed(info: dict, output_path: str):
    """
    Generates an official-looking, formatted title deed PDF using ReportLab.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        'GovHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F172A')
    )
    
    sub_header = ParagraphStyle(
        'GovSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#334155')
    )

    body_style = ParagraphStyle(
        'DeedBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    bold_body = ParagraphStyle(
        'DeedBoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Header Box
    elements.append(Paragraph("GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT", header_style))
    elements.append(Paragraph("TITLE DEED OF SALE / ABSOLUTE CONVEYANCE DEED", sub_header))
    elements.append(Paragraph(f"Document No: {info['doc_number']} | {info['book']} | {info['sro']}", sub_header))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=2, spaceAfter=8))

    # General Information Table
    gen_data = [
        [
            Paragraph("<b>DISTRICT:</b>", bold_body), Paragraph(info["district"], body_style),
            Paragraph("<b>TALUK:</b>", bold_body), Paragraph(info["taluk"], body_style)
        ],
        [
            Paragraph("<b>VILLAGE:</b>", bold_body), Paragraph(info["village"], body_style),
            Paragraph("<b>SURVEY NUMBER:</b>", bold_body), Paragraph(f"<b><font color='#047857'>{info['survey_number']}</font></b>", bold_body)
        ]
    ]

    t_gen = Table(gen_data, colWidths=[90, 175, 100, 175])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_gen)
    elements.append(Spacer(1, 10))

    # Schedule of Property Table
    elements.append(Paragraph("<b>SCHEDULE OF PROPERTY & AREA EXTENT</b>", bold_body))
    elements.append(Spacer(1, 4))
    
    sched_data = [
        [Paragraph("<b>Area Extent:</b>", bold_body), Paragraph(info["area_sqft"], body_style)],
        [Paragraph("<b>GPS Coordinates:</b>", bold_body), Paragraph(info["gps"], body_style)],
        [Paragraph("<b>Boundary (North):</b>", bold_body), Paragraph(info["boundaries"]["north"], body_style)],
        [Paragraph("<b>Boundary (South):</b>", bold_body), Paragraph(info["boundaries"]["south"], body_style)],
        [Paragraph("<b>Boundary (East):</b>", bold_body), Paragraph(info["boundaries"]["east"], body_style)],
        [Paragraph("<b>Boundary (West):</b>", bold_body), Paragraph(info["boundaries"]["west"], body_style)],
    ]
    t_sched = Table(sched_data, colWidths=[120, 420])
    t_sched.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_sched)
    elements.append(Spacer(1, 10))

    # Purchaser & Titleholder Info
    elements.append(Paragraph("<b>TITLEHOLDER & REGISTRATION PARTICULARS</b>", bold_body))
    elements.append(Spacer(1, 4))
    
    purchaser_data = [
        [Paragraph("<b>Purchaser Name:</b>", bold_body), Paragraph(info["purchaser"], body_style)],
        [Paragraph("<b>Parent / Spouse:</b>", bold_body), Paragraph(info["father_name"], body_style)],
        [Paragraph("<b>Aadhaar ID (Masked):</b>", bold_body), Paragraph(f"XXXX-XXXX-{info['aadhaar_masked'][-4:]}", body_style)],
        [Paragraph("<b>Cryptographic Root:</b>", bold_body), Paragraph(f"<font face='Courier' size='7.5'>{info['registered_hash']}</font>", body_style)],
    ]
    t_purchaser = Table(purchaser_data, colWidths=[120, 420])
    t_purchaser.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_purchaser)
    elements.append(Spacer(1, 12))

    # Legal Disclaimer / Seal Footer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_JUSTIFY
    )
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(
        "OFFICIAL REVENUE DOCUMENT: Issued by Registration Department, Government of Tamil Nadu under the Registration Act, 1908. "
        "Verified and secured via PlotProof Cadastral Integrity & Blockchain Anchoring Protocol. "
        "Any boundary collision or unauthorized alteration is cryptographically detected.",
        disclaimer_style
    ))

    doc.build(elements)


def generate_all_sample_deeds():
    """
    Generates all sample and default demonstration deeds in both .txt and .pdf format.
    """
    uploads_dir = str(UPLOAD_DIR)
    os.makedirs(uploads_dir, exist_ok=True)

    for key, info in SAMPLE_DEEDS_INFO.items():
        # 1. Generate text deed
        txt_path = os.path.join(uploads_dir, info["filename_txt"])
        txt_content = f"""{info['title']}
Document Registration Number: {info['doc_number']}
{info['book']}
{info['sro']}

DISTRICT: {info['district']}
TALUK: {info['taluk']}
VILLAGE: {info['village']}
SURVEY NUMBER: {info['survey_number']}

EXTENT AND MEASUREMENT OF PROPERTY:
All that piece and parcel of land bearing Survey No: {info['survey_number']}, measuring an area of {info['area_sqft']}.

BOUNDARIES:
North by: {info['boundaries']['north']}
South by: {info['boundaries']['south']}
East by: {info['boundaries']['east']}
West by: {info['boundaries']['west']}

COORDINATES:
GPS Reference Bounds: {info['gps']}

PURCHASER / TITLE HOLDER:
Name: {info['purchaser']}
Son/Daughter of: {info['father_name']}
Aadhaar UID: {info['aadhaar_masked']}

REGISTERED HASH COMMITMENT:
{info['registered_hash']}
"""
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_content)

        # 2. Generate PDF deed
        pdf_path = os.path.join(uploads_dir, info["filename_pdf"])
        try:
            generate_sample_pdf_deed(info, pdf_path)
        except Exception as e:
            print(f"Error generating PDF {pdf_path}: {e}")

    # Also create standard alias names for instant access
    aliases = {
        "sample_default_deed.pdf": "TitleDeed_Genuine.pdf",
        "demo_collision_deed.pdf": "TitleDeed_Collision.pdf",
        "demo_tampered_deed.pdf": "TitleDeed_Tampered.pdf",
        "sample_genuine_142_3A.txt": "default_demonstration_deed.txt",
    }
    for src, alias in aliases.items():
        src_p = os.path.join(uploads_dir, src)
        alias_p = os.path.join(uploads_dir, alias)
        if os.path.exists(src_p):
            import shutil
            shutil.copyfile(src_p, alias_p)


if __name__ == "__main__":
    generate_all_sample_deeds()
    print("All sample and default demonstration deeds successfully generated.")
