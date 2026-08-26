from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.deed import BlockchainRecord, VerificationRecord, Document

router = APIRouter(prefix="/api/blockchain", tags=["Blockchain Trust Layer"])

@router.get("/{verification_id}")
async def get_blockchain_record(verification_id: str, db: Session = Depends(get_db)):
    """
    Returns the immutable blockchain audit receipt for a verified document.
    """
    bc = db.query(BlockchainRecord).filter(BlockchainRecord.verification_id == verification_id).first()
    if not bc:
        raise HTTPException(status_code=404, detail="Blockchain record not found")

    return {
        "verification_id": bc.verification_id,
        "document_hash": bc.document_hash,
        "transaction_hash": bc.transaction_hash,
        "block_number": bc.block_number,
        "contract_address": bc.contract_address,
        "network": bc.network,
        "timestamp": bc.timestamp.isoformat(),
        "status": bc.status,
        "smart_contract_method": "registerDocument(bytes32,string)",
        "explorer_url": f"https://amoy.polygonscan.com/tx/{bc.transaction_hash}"
    }
