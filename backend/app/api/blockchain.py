from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.deed import BlockchainRecord
from app.services.document_service import DocumentService
from app.blockchain.service import BlockchainService

router = APIRouter(tags=["Blockchain & Smart Contract"])

blockchain_service = BlockchainService()
doc_service = DocumentService()


# --- LAYER 8 REST ENDPOINTS (Section 16) ---

@router.post("/api/v1/documents/{document_id}/blockchain/anchor")
def anchor_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Anchors verified title record onto Polygon Blockchain (Section 10 & 17).
    Enforces strict prerequisite validation: Integrity PASS, GIS PASS, ZK proof VALID.
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return blockchain_service.anchor_verification(
        db=db,
        document_id=doc.id,
        actor_id=current_user.id,
    )


@router.get("/api/v1/documents/{document_id}/blockchain")
def get_document_anchor(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the blockchain anchor receipt for a document (Section 16).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    anchor = blockchain_service.get_anchor(db=db, document_id=doc.id)
    if not anchor:
        raise HTTPException(status_code=404, detail="Blockchain anchor record not found for this document")

    return {
        "document_id": doc.id,
        "verification_id": anchor.verification_id,
        "transaction_hash": anchor.transaction_hash,
        "block_number": anchor.block_number,
        "contract_address": anchor.contract_address,
        "network": anchor.network,
        "status": anchor.status,
        "created_at": anchor.created_at.isoformat() if anchor.created_at else None,
    }


@router.get("/api/v1/verification/{verification_id}")
def verify_against_blockchain_endpoint(
    verification_id: str,
    db: Session = Depends(get_db),
):
    """
    Public verifier endpoint cross-checking database against Polygon blockchain state (Section 19 & 20).
    Detects database tampering if a database record has been modified after on-chain anchoring.
    """
    return blockchain_service.verify_against_blockchain(db=db, verification_id=verification_id)


# --- LEGACY ENDPOINT (Backwards Compatibility) ---

@router.get("/api/blockchain/{verification_id}")
def get_blockchain_record_legacy(verification_id: str, db: Session = Depends(get_db)):
    """
    Legacy blockchain record retrieval for earlier frontend routes.
    """
    bc = db.query(BlockchainRecord).filter(BlockchainRecord.verification_id == verification_id).first()
    if bc:
        return {
            "verification_id": bc.verification_id,
            "document_hash": bc.document_hash,
            "transaction_hash": bc.transaction_hash,
            "block_number": bc.block_number,
            "contract_address": bc.contract_address,
            "network": bc.network,
            "timestamp": bc.timestamp.isoformat(),
            "status": bc.status,
            "smart_contract_method": "anchorVerification(bytes32,bytes32,bytes32)",
            "explorer_url": f"https://amoy.polygonscan.com/tx/{bc.transaction_hash}",
        }

    anchor = db.scalar(select(BlockchainAnchor).where(BlockchainAnchor.verification_id == verification_id))
    if anchor:
        return {
            "verification_id": anchor.verification_id,
            "document_hash": anchor.transaction_hash,
            "transaction_hash": anchor.transaction_hash,
            "block_number": anchor.block_number,
            "contract_address": anchor.contract_address,
            "network": anchor.network,
            "timestamp": anchor.created_at.isoformat() if anchor.created_at else None,
            "status": anchor.status,
            "smart_contract_method": "anchorVerification(bytes32,bytes32,bytes32)",
            "explorer_url": f"https://amoy.polygonscan.com/tx/{anchor.transaction_hash}",
        }

    raise HTTPException(status_code=404, detail="Blockchain record not found")
