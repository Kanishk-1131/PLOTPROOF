import json
import os
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.deed import Plot, Document, LandRecord, VerificationRecord, BlockchainRecord
from app.core.security import hash_password
from app.database.connection import SessionLocal, init_db

def seed_database():
    init_db()
    db: Session = SessionLocal()

    # 1. Seed Users
    if db.query(User).count() == 0:
        default_pwd = hash_password("PlotProof2026!")
        users = [
            User(full_name="Ramanathan K. S.", email="citizen@plotproof.gov.in", password_hash=default_pwd, role=UserRole.CITIZEN, is_verified=True),
            User(full_name="Sub-Registrar Officer Tambaram", email="registrar@tn.gov.in", password_hash=default_pwd, role=UserRole.REGISTRAR, is_verified=True),
            User(full_name="HDFC Land Loan Audit Officer", email="auditor@hdfcbank.com", password_hash=default_pwd, role=UserRole.BANK_OFFICER, is_verified=True),
            User(full_name="System Administrator", email="admin@plotproof.gov.in", password_hash=default_pwd, role=UserRole.ADMIN, is_verified=True),
        ]
        db.add_all(users)
        db.commit()

    # 2. Seed Cadastral Reference Parcels (Selaiyur, Tambaram, Chennai)
    # Coordinates in [lng, lat] for GeoJSON
    plots_data = [
        {
            "plot_id": "TN-CHE-TAM-142-01",
            "survey_number": "142/1",
            "village": "Selaiyur",
            "taluk": "Tambaram",
            "district": "Chennai",
            "area_sqft": 2400.0,
            "area_sqm": 222.96,
            "status": "REGISTERED",
            "owner": "R. M**********",
            "coordinates": [
                [80.1465, 12.9249],
                [80.1465, 12.9255],
                [80.1471, 12.9255],
                [80.1471, 12.9249],
                [80.1465, 12.9249]
            ]
        },
        {
            "plot_id": "TN-CHE-TAM-142-02",
            "survey_number": "142/2",
            "village": "Selaiyur",
            "taluk": "Tambaram",
            "district": "Chennai",
            "area_sqft": 4800.0,
            "area_sqm": 445.93,
            "status": "REGISTERED",
            "owner": "HIGHWAY / GOVT ROAD",
            "coordinates": [
                [80.1465, 12.9255],
                [80.1465, 12.9261],
                [80.1485, 12.9261],
                [80.1485, 12.9255],
                [80.1465, 12.9255]
            ]
        },
        {
            "plot_id": "TN-CHE-TAM-142-03A",
            "survey_number": "142/3A",
            "village": "Selaiyur",
            "taluk": "Tambaram",
            "district": "Chennai",
            "area_sqft": 2400.0,
            "area_sqm": 222.96,
            "status": "REGISTERED",
            "owner": "K. S. **********",
            "coordinates": [
                [80.1472, 12.9249],
                [80.1472, 12.9255],
                [80.1478, 12.9255],
                [80.1478, 12.9249],
                [80.1472, 12.9249]
            ]
        },
        {
            "plot_id": "TN-CHE-TAM-142-04",
            "survey_number": "142/4",
            "village": "Selaiyur",
            "taluk": "Tambaram",
            "district": "Chennai",
            "area_sqft": 2400.0,
            "area_sqm": 222.96,
            "status": "REGISTERED",
            "owner": "S. V**********",
            "coordinates": [
                [80.1472, 12.9243],
                [80.1472, 12.9249],
                [80.1478, 12.9249],
                [80.1478, 12.9243],
                [80.1472, 12.9243]
            ]
        },
        {
            "plot_id": "TN-CHE-TAM-142-05",
            "survey_number": "142/5",
            "village": "Selaiyur",
            "taluk": "Tambaram",
            "district": "Chennai",
            "area_sqft": 3000.0,
            "area_sqm": 278.71,
            "status": "REGISTERED",
            "owner": "P. N**********",
            "coordinates": [
                [80.1479, 12.9249],
                [80.1479, 12.9255],
                [80.1485, 12.9255],
                [80.1485, 12.9249],
                [80.1479, 12.9249]
            ]
        }
    ]

    for p in plots_data:
        existing = db.query(Plot).filter(Plot.plot_id == p["plot_id"]).first()
        geojson_geom = {
            "type": "Polygon",
            "coordinates": [p["coordinates"]]
        }
        wkt_coords = ", ".join([f"{pt[0]} {pt[1]}" for pt in p["coordinates"]])
        wkt_geom = f"POLYGON(({wkt_coords}))"

        if not existing:
            plot_obj = Plot(
                plot_id=p["plot_id"],
                survey_number=p["survey_number"],
                village=p["village"],
                taluk=p["taluk"],
                district=p["district"],
                area_sqft=p["area_sqft"],
                area_sqm=p["area_sqm"],
                geometry_wkt=wkt_geom,
                geometry_geojson=json.dumps(geojson_geom),
                owner_name_masked=p["owner"],
                status=p["status"]
            )
            db.add(plot_obj)
        else:
            existing.geometry_geojson = json.dumps(geojson_geom)
            existing.geometry_wkt = wkt_geom

    db.commit()

    # 3. Create Sample Deeds in static/uploads
    from app.utils.paths import UPLOAD_DIR
    uploads_dir = str(UPLOAD_DIR)

    genuine_text = """GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT
TITLE DEED OF SALE / CONVEYANCE DEED
Document Registration Number: 4821/2024
Book 1, Volume 912, Pages 101 to 114
Sub-Registrar Office: Tambaram

DISTRICT: Chennai
TALUK: Tambaram
VILLAGE: Selaiyur Village
SURVEY NUMBER: 142/3A

EXTENT AND MEASUREMENT OF PROPERTY:
All that piece and parcel of land bearing Survey No: 142/3A, measuring an area of 2400 Sq.ft (equivalent to 222.96 Sq.meters / 5.5 Cents).

BOUNDARIES:
North by: Survey No 142/2 (Road 30ft width)
South by: Survey No 142/4 (Vacant Plot)
East by: Survey No 142/3B (Adjacent Plot)
West by: Survey No 142/1 (Residential Property)

COORDINATES:
GPS Reference Bounds: 12.9249 N, 80.1472 E to 12.9255 N, 80.1478 E

PURCHASER / TITLE HOLDER:
Name: K. S. Ramanathan
Son of: Late K. Sundaram
Aadhaar UID: 5412-8823-8912

REGISTERED HASH COMMITMENT:
7c3e8f2c9a620d41e7845f096231ba4190284e91240185e2b028941785e091ad
"""
    with open(os.path.join(uploads_dir, "sample_genuine_142_3A.txt"), "w", encoding="utf-8") as f:
        f.write(genuine_text)

    tampered_text = """GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT
TITLE DEED OF SALE / CONVEYANCE DEED
Document Registration Number: 4821/2024
Sub-Registrar Office: Tambaram

DISTRICT: Chennai
TALUK: Tambaram
VILLAGE: Selaiyur Village
SURVEY NUMBER: 142/3A

EXTENT AND MEASUREMENT OF PROPERTY:
All that piece and parcel of land bearing Survey No: 142/3A, measuring an area of 3400 Sq.ft (equivalent to 315.87 Sq.meters).

BOUNDARIES:
North by: Survey No 142/2 (Road 30ft width)
South by: Survey No 142/4 (Vacant Plot)
East by: Survey No 142/3B (Adjacent Plot)
West by: Survey No 142/1 (Residential Property)

COORDINATES:
GPS Reference Bounds: 12.9249 N, 80.1472 E to 12.9255 N, 80.1478 E

PURCHASER / TITLE HOLDER:
Name: K. S. Ramanathan
Son of: Late K. Sundaram
Aadhaar UID: 5412-8823-8912
"""
    with open(os.path.join(uploads_dir, "sample_tampered_area.txt"), "w", encoding="utf-8") as f:
        f.write(tampered_text)

    collision_text = """GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT
TITLE DEED OF SALE / CONVEYANCE DEED
Document Registration Number: 5109/2024
Sub-Registrar Office: Tambaram

DISTRICT: Chennai
TALUK: Tambaram
VILLAGE: Selaiyur Village
SURVEY NUMBER: 142/3B

EXTENT AND MEASUREMENT OF PROPERTY:
All that piece and parcel of land bearing Survey No: 142/3B, measuring an area of 2400 Sq.ft (equivalent to 222.96 Sq.meters).

BOUNDARIES:
North by: Survey No 142/2
South by: Survey No 142/4
East by: Survey No 142/5
West by: Survey No 142/3A

COORDINATES:
GPS Reference Bounds: 12.9252 N, 80.1476 E to 12.9258 N, 80.1482 E

PURCHASER / TITLE HOLDER:
Name: M. Vijay Anand
Son of: R. Mohan
Aadhaar UID: 8721-3312-9014
"""
    with open(os.path.join(uploads_dir, "sample_collision_142_3B.txt"), "w", encoding="utf-8") as f:
        f.write(collision_text)

    # 4. Seed Seed Initial Verification History for Rich Dashboard Analytics
    if db.query(VerificationRecord).count() == 0:
        base_time = datetime.utcnow() - timedelta(days=5)
        seed_history = [
            ("PP-2026-00139", "142/1", "VERIFIED", 96.5, False, False, "7c3e8f2c9a11..."),
            ("PP-2026-00140", "142/2", "VERIFIED", 98.0, False, False, "9f4e2a1b8c22..."),
            ("PP-2026-00141", "142/3B", "SPATIAL_COLLISION", 45.0, True, False, "3b1d7e8a9f33..."),
            ("PP-2026-00138", "142/4", "MANUAL_REVIEW", 68.0, False, False, "6a2c9f1e4d44..."),
            ("PP-2026-00137", "142/3A-MOD", "TAMPER_ALERT", 35.0, False, True, "e4d2a9f1b755..."),
        ]

        for v_id, s_no, status, score, coll, tamp, d_hash in seed_history:
            doc_file = os.path.join(uploads_dir, f"{v_id}.txt")
            sample_content = tampered_text if tamp else (collision_text if coll else genuine_text)
            with open(doc_file, "w", encoding="utf-8") as f:
                f.write(sample_content)

            d_sha = hashlib.sha256(v_id.encode()).hexdigest()
            doc = Document(
                owner_user_id=1,
                verification_id=v_id,
                file_path=doc_file,
                file_name=f"Deed_{s_no.replace('/', '_')}.pdf",
                storage_key=f"seed/{v_id}.pdf",
                sha256=d_sha,
                file_hash=d_sha,
                file_size=245890,
                mime_type="application/pdf",
                ocr_raw_text=f"Sample Deed for {s_no}",
                created_at=base_time
            )
            db.add(doc)
            db.flush()


            verif = VerificationRecord(
                verification_id=v_id,
                document_id=doc.id,
                ocr_score=95.0,
                spatial_score=15.0 if coll else 98.0,
                authenticity_score=0.0 if tamp else 100.0,
                privacy_score=95.0,
                overall_score=score,
                status=status,
                collision_detected=coll,
                tamper_detected=tamp,
                created_at=base_time
            )
            db.add(verif)

            bc = BlockchainRecord(
                verification_id=v_id,
                document_hash=hashlib.sha256(v_id.encode()).hexdigest(),
                transaction_hash=f"0x8a91f4b23c{v_id[-5:].lower()}77e091bfa3c612db9841289cf1a",
                block_number=18942000 + int(v_id[-3:]),
                created_at=base_time
            )
            db.add(bc)
            base_time += timedelta(hours=14)

        db.commit()

    db.close()
    print("Database successfully seeded with cadastral plots, test deeds, and historical audits.")

if __name__ == "__main__":
    seed_database()
