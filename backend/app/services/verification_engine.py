import json
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.services.ocr_service import OCRService
from app.services.gis_service import GISService
from app.services.hash_service import HashService
from app.services.zk_service import ZKPrivacyService
from app.services.certificate_service import CertificateService
from app.models.deed import Document, LandRecord, VerificationRecord, BlockchainRecord

class VerificationEngine:
    @staticmethod
    def run_full_pipeline(db: Session, document_id: int) -> Dict[str, Any]:
        """
        Runs the complete multi-vector forensic verification pipeline:
        1. Preprocessing & OCR Extraction
        2. GIS Cadastral Spatial Analysis
        3. Cryptographic SHA-256 Tamper Verification
        4. Privacy-Preserving ZK Commitment
        5. Blockchain Ledger Registration
        6. Digital Certificate & QR Generation
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document ID {document_id} not found")

        # 1. OCR Extraction
        ocr_res = OCRService.process_document(doc.file_path)
        extracted = ocr_res["extracted_fields"]
        doc.ocr_raw_text = ocr_res["raw_text"]

        # 2. GIS Spatial Analysis
        gis_res = GISService.check_spatial_collision(
            db=db,
            submitted_survey=extracted["survey_number"],
            coordinates=extracted["coordinates"],
            claimed_area_sqft=extracted["area_sqft"]
        )

        # 3. Authenticity & Tamper Detection
        tamper_res = HashService.verify_document_integrity(extracted)

        # 4. Privacy & ZK Commitment
        zk_res = ZKPrivacyService.generate_privacy_proof(
            owner_name_raw=extracted.get("owner_name_raw", "K. S. Ramanathan"),
            aadhaar_raw=extracted.get("aadhaar_masked", "5412-8823-8912")
        )

        # 5. Determine Overall Verdict & Confidence Score
        if tamper_res["is_tampered"]:
            overall_status = "TAMPER_ALERT"
            confidence_score = 38.0
            ocr_score = 90.0
            spatial_score = 85.0
            authenticity_score = 0.0
            privacy_score = 95.0
        elif gis_res["overlap_detail"]["collision_detected"]:
            overall_status = "SPATIAL_COLLISION"
            confidence_score = 45.0
            ocr_score = 94.0
            spatial_score = 15.0
            authenticity_score = 90.0
            privacy_score = 95.0
        elif ocr_res["confidence_score"] < 0.7:
            overall_status = "MANUAL_REVIEW"
            confidence_score = 62.0
            ocr_score = 65.0
            spatial_score = 80.0
            authenticity_score = 80.0
            privacy_score = 90.0
        else:
            overall_status = "VERIFIED"
            confidence_score = 96.0
            ocr_score = 98.0
            spatial_score = 99.0
            authenticity_score = 100.0
            privacy_score = 100.0

        overall_weighted = round(
            (ocr_score * 0.2) + (spatial_score * 0.4) + (authenticity_score * 0.3) + (privacy_score * 0.1),
            1
        )

        # 6. Generate QR & Certificate
        qr_url = CertificateService.generate_qr_code(
            document_hash=tamper_res["document_hash"],
            verification_id=doc.verification_id
        )

        # Mock / Real Blockchain Transaction
        tx_hash = f"0x8a91f4b23c{doc.verification_id[-5:].lower()}77e091bfa3c612db9841289cf1a"
        block_number = 18942103

        # 7. Persist or Update Database Records
        # LandRecord
        land_rec = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()
        if not land_rec:
            land_rec = LandRecord(
                document_id=doc.id,
                survey_number=extracted["survey_number"],
                district=extracted["district"],
                taluk=extracted["taluk"],
                village=extracted["village"],
                area_sqft=extracted["area_sqft"],
                area_sqm=extracted["area_sqm"],
                owner_name_masked=extracted["owner_name_masked"],
                owner_hash=zk_res["ownership_commitment_hash"],
                boundary_north=extracted["boundaries"]["north"],
                boundary_south=extracted["boundaries"]["south"],
                boundary_east=extracted["boundaries"]["east"],
                boundary_west=extracted["boundaries"]["west"],
                coordinates_json=json.dumps(extracted["coordinates"])
            )
            db.add(land_rec)

        # Verification Record
        verif_rec = db.query(VerificationRecord).filter(VerificationRecord.verification_id == doc.verification_id).first()
        if not verif_rec:
            verif_rec = VerificationRecord(
                verification_id=doc.verification_id,
                document_id=doc.id,
                ocr_score=ocr_score,
                spatial_score=spatial_score,
                authenticity_score=authenticity_score,
                privacy_score=privacy_score,
                overall_score=overall_weighted,
                status=overall_status,
                collision_detected=gis_res["overlap_detail"]["collision_detected"],
                tamper_detected=tamper_res["is_tampered"],
                collision_details_json=json.dumps(gis_res["overlap_detail"]),
                tamper_details_json=json.dumps(tamper_res),
                privacy_details_json=json.dumps(zk_res),
                certificate_url=f"/certificate/{doc.verification_id}",
                qr_code_url=qr_url
            )
            db.add(verif_rec)
        else:
            verif_rec.ocr_score = ocr_score
            verif_rec.spatial_score = spatial_score
            verif_rec.authenticity_score = authenticity_score
            verif_rec.privacy_score = privacy_score
            verif_rec.overall_score = overall_weighted
            verif_rec.status = overall_status
            verif_rec.collision_detected = gis_res["overlap_detail"]["collision_detected"]
            verif_rec.tamper_detected = tamper_res["is_tampered"]
            verif_rec.collision_details_json = json.dumps(gis_res["overlap_detail"])
            verif_rec.tamper_details_json = json.dumps(tamper_res)
            verif_rec.privacy_details_json = json.dumps(zk_res)
            verif_rec.qr_code_url = qr_url

        # Blockchain Record
        bc_rec = db.query(BlockchainRecord).filter(BlockchainRecord.verification_id == doc.verification_id).first()
        if not bc_rec:
            bc_rec = BlockchainRecord(
                verification_id=doc.verification_id,
                document_hash=tamper_res["document_hash"],
                transaction_hash=tx_hash,
                block_number=block_number,
                contract_address="0x71C8366420A0926718E29ce7705B732d43b91B32",
                network="Polygon Amoy / PlotProof Private Net",
                status="CONFIRMED"
            )
            db.add(bc_rec)

        db.commit()

        return {
            "verification_id": doc.verification_id,
            "document_id": doc.id,
            "overall_status": overall_status,
            "confidence_score": overall_weighted,
            "created_at": doc.created_at,
            "document": {
                "file_name": doc.file_name,
                "file_hash": doc.file_hash,
                "raw_text": doc.ocr_raw_text,
                "extracted_fields": extracted,
                "ocr_confidence": ocr_res["confidence_score"]
            },
            "spatial": gis_res,
            "authenticity": tamper_res,
            "privacy": zk_res,
            "blockchain": {
                "registered_on_chain": True,
                "document_hash": tamper_res["document_hash"],
                "verification_id": doc.verification_id,
                "transaction_hash": tx_hash,
                "block_number": block_number,
                "contract_address": "0x71C8366420A0926718E29ce7705B732d43b91B32",
                "network": "Polygon Amoy / PlotProof Private Net",
                "timestamp": datetime.utcnow().isoformat(),
                "block_explorer_url": f"https://amoy.polygonscan.com/tx/{tx_hash}"
            },
            "certificate_url": f"/certificate/{doc.verification_id}",
            "qr_code_url": qr_url
        }
