from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.orchestrator import OrchestratorService


class VerificationEngine:
    @staticmethod
    def run_full_pipeline(db: Session, document_id: int) -> Dict[str, Any]:
        """
        Authoritative entry point for verification pipeline.
        Delegates execution to the 9-stage OrchestratorService and returns
        the unified forensic VerificationReport.
        """
        orchestrator = OrchestratorService()
        
        # 1. Start or resume verification orchestration
        verif = orchestrator.start_verification(db=db, document_id=document_id)
        
        # 2. Return unified forensic report
        return orchestrator.build_frontend_report(db=db, verification_id=verif.verification_id)

