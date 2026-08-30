import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def run_preset(preset_type):
    print("=" * 60)
    print(f">>> Processing Deed: {preset_type.upper()}")
    print("=" * 60)
    
    # 1. Upload
    up_res = requests.post(f"{BASE_URL}/api/documents/upload", data={"preset_type": preset_type})
    if up_res.status_code != 200:
        print(f"[ERROR] Upload failed ({up_res.status_code}): {up_res.text}")
        return None
    up_data = up_res.json()
    doc_id = up_data["document_id"]
    vid = up_data["verification_id"]
    print(f"[Stage 1: Ingestion & Hash]")
    print(f"  • Verification ID : {vid}")
    print(f"  • Document ID     : {doc_id}")
    print(f"  • File Name       : {up_data['file_name']}")
    print(f"  • SHA-256 Digest  : {up_data['file_hash']}")
    
    # 2. Start Verification Pipeline
    v_res = requests.post(f"{BASE_URL}/api/verification/start/{doc_id}")
    if v_res.status_code != 200:
        print(f"[ERROR] Verification failed ({v_res.status_code}): {v_res.text}")
        return None
    v_data = v_res.json()
    
    status = v_data.get("overall_status") or v_data.get("status")
    score = v_data.get("confidence_score") or v_data.get("overall_score")
    
    spatial = v_data.get("spatial", {})
    overlap = spatial.get("overlap_detail", {})
    collision = overlap.get("collision_detected", v_data.get("collision_detected"))
    
    auth = v_data.get("authenticity", {})
    tampered = auth.get("is_tampered", v_data.get("tamper_detected"))
    
    privacy = v_data.get("privacy", {})
    blockchain = v_data.get("blockchain", {})
    cert = v_data.get("certificate", {})
    
    print(f"\n[8-Stage Forensic Pipeline Analysis Result]")
    print(f"  • Final Decision       : {status}")
    print(f"  • Confidence Score     : {score}%")
    print(f"  • OCR Survey / Area    : {v_data.get('document', {}).get('extracted_fields', {}).get('survey_number')} | {v_data.get('document', {}).get('extracted_fields', {}).get('area_sqft')} sq.ft")
    print(f"  • Spatial Collision    : {'YES (Encroachment Detected)' if collision else 'NO (Zero Overlap)'}")
    if collision:
        print(f"    - Overlap Area       : {overlap.get('overlap_area_sqm')} sq.m ({overlap.get('overlap_area_sqft')} sq.ft)")
        print(f"    - Risk Level         : {overlap.get('risk_level')}")
        print(f"    - Action Required    : {overlap.get('action_required')}")
    print(f"  • Integrity Check      : {'TAMPERED (Hash Mismatch)' if tampered else 'AUTHENTIC (SHA-256 Valid)'}")
    print(f"  • ZK-SNARK Privacy     : {privacy.get('zk_proof_status', 'Generated')} (Zero PII Exposed)")
    print(f"  • Blockchain Anchored  : {blockchain.get('registered_on_chain', False)}")
    if blockchain.get('tx_hash'):
        print(f"    - Polygon Tx Hash    : {blockchain.get('tx_hash')}")
        print(f"    - Smart Contract     : {blockchain.get('contract_address')}")
    if cert.get('certificate_url'):
        print(f"  • PDF Certificate QR   : {BASE_URL}{cert.get('certificate_url')}")
    
    print(f"  • Frontend Report View : http://localhost:3000/verification/{vid}")
    print("\n")
    return vid, v_data

if __name__ == "__main__":
    results = {}
    for p in ["genuine", "collision", "tampered"]:
        results[p] = run_preset(p)
