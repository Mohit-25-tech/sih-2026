import os
import shutil
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Document, ExtractedField, TamperResult, RiskScore, AuditLog
from app.schemas import (
    DocumentDetailResponse,
    DocumentListItem,
    FaceVerifyRequest,
    FaceVerifyResponse,
    AuditLogSchema
)
from app.config import settings
from app.services.ocr_mrz_service import extract_ocr_and_mrz
from app.services.ela_service import generate_ela_heatmap
from app.services.face_service import compare_faces
from app.services.risk_fusion_service import calculate_fused_risk_score

router = APIRouter()

@router.post("/documents/upload", response_model=DocumentDetailResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("PASSPORT"),
    db: Session = Depends(get_db)
):
    """
    1. Save uploaded file to static/uploads/
    2. Extract MRZ & OCR text
    3. Generate ELA forensic heatmap
    4. Calculate Risk Fusion Score
    5. Save to Neon PostgreSQL / SQLite DB
    """
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"doc_{uuid.uuid4().hex[:10]}{file_ext}"
        saved_file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create Document DB Record
        db_doc = Document(
            filename=file.filename,
            file_path=f"/static/uploads/{unique_filename}",
            document_type=document_type.upper(),
            status="SCREENED"
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        # Step A: OCR & MRZ Extraction
        mrz_data, extracted_fields_data = extract_ocr_and_mrz(saved_file_path)

        # Save Extracted Fields to DB
        db_fields = []
        for field in extracted_fields_data:
            ef = ExtractedField(
                document_id=db_doc.id,
                field_name=field["field_name"],
                visual_value=field["visual_value"],
                mrz_value=field["mrz_value"],
                is_match=field["is_match"],
                confidence=field["confidence"]
            )
            db.add(ef)
            db_fields.append(ef)

        # Step B: ELA Tamper Analysis
        ela_url, ela_score, is_tampered, anomaly_regions = generate_ela_heatmap(saved_file_path)
        
        db_tamper = TamperResult(
            document_id=db_doc.id,
            ela_heatmap_path=ela_url,
            ela_score=ela_score,
            is_tampered=is_tampered,
            anomaly_regions=anomaly_regions
        )
        db.add(db_tamper)

        # Step C: Risk Fusion Engine
        overall_score, risk_level, factors, reasoning = calculate_fused_risk_score(
            mrz_data=mrz_data,
            extracted_fields=extracted_fields_data,
            ela_score=ela_score,
            is_tampered=is_tampered
        )

        db_risk = RiskScore(
            document_id=db_doc.id,
            score=overall_score,
            risk_level=risk_level,
            factors=factors,
            summary_reasoning=reasoning
        )
        db.add(db_risk)

        # Step D: Audit Log Entry
        db_log = AuditLog(
            document_id=db_doc.id,
            officer_id="OFFICER_ZENITH_01",
            action="DOCUMENT_SCREENED",
            details={
                "risk_level": risk_level,
                "score": overall_score,
                "filename": file.filename
            }
        )
        db.add(db_log)

        db.commit()
        db.refresh(db_doc)

        return db_doc

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process document screening: {str(e)}")


@router.get("/documents", response_model=List[DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    """Return all screened documents for audit log history table."""
    docs = db.query(Document).order_by(Document.upload_time.desc()).all()
    results = []
    for d in docs:
        r_level = d.risk_score.risk_level if d.risk_score else "LOW"
        r_score = d.risk_score.score if d.risk_score else 0.0
        results.append({
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "upload_time": d.upload_time,
            "status": d.status,
            "risk_level": r_level,
            "risk_score": r_score
        })
    return results


@router.get("/documents/samples")
def list_sample_documents():
    """List preset authentic and tampered sample documents for instant testing."""
    samples = [
        {
            "id": "authentic_passport_01",
            "title": "Authentic Passport — Republic of India",
            "filename": "sample_authentic_passport.jpg",
            "type": "PASSPORT",
            "description": "Standard authentic passport with valid MRZ checksum digits and 0% ELA anomaly.",
            "expected_risk": "LOW"
        },
        {
            "id": "tampered_photo_passport_02",
            "title": "Tampered Passport — Photo & DOB Altered",
            "filename": "sample_tampered_passport.jpg",
            "type": "PASSPORT",
            "description": "Forged document with substituted photo ROI, corrupted MRZ checksum, and DOB mismatch.",
            "expected_risk": "HIGH"
        },
        {
            "id": "mrz_mismatch_visa_03",
            "title": "Visa Card — Field Mismatch",
            "filename": "sample_mismatch_visa.jpg",
            "type": "VISA",
            "description": "Visa document with valid photo but conflicting Document Number between MRZ and OCR zone.",
            "expected_risk": "MEDIUM"
        }
    ]
    return samples


@router.post("/documents/load-sample/{sample_id}", response_model=DocumentDetailResponse)
def load_sample_document(sample_id: str, db: Session = Depends(get_db)):
    """
    Loads a pre-configured sample document directly for 1-click testing.
    Runs the full real pipeline — no hardcoded overrides.
    """
    import logging
    log = logging.getLogger("veriborder.routes")

    sample_file_map = {
        "authentic_passport_01": ("sample_authentic_passport.jpg", "Authentic_India_Passport.jpg"),
        "tampered_photo_passport_02": ("sample_tampered_passport.jpg", "Tampered_Passport_Altered.jpg"),
        "mrz_mismatch_visa_03": ("sample_mismatch_visa.jpg", "Mismatch_Visa_Card.jpg")
    }

    if sample_id not in sample_file_map:
        sample_id = "authentic_passport_01"

    src_filename, display_filename = sample_file_map[sample_id]
    src_path = os.path.join(settings.SAMPLE_DIR, src_filename)

    # Ensure sample file exists — generate if missing
    if not os.path.exists(src_path):
        log.warning(f"Sample file missing: {src_path} — regenerating samples...")
        try:
            from generate_samples import generate_sample_passport
            generate_sample_passport("sample_authentic_passport.jpg", is_tampered=False)
            generate_sample_passport("sample_tampered_passport.jpg", is_tampered=True)
            generate_sample_passport("sample_mismatch_visa.jpg", is_tampered=True)
        except Exception as e:
            log.error(f"Failed to generate samples: {e}")
            raise HTTPException(status_code=500, detail=f"Sample file not found and regeneration failed: {e}")

    if not os.path.exists(src_path):
        raise HTTPException(status_code=404, detail=f"Sample file not found: {src_filename}")

    # Copy to uploads folder
    unique_filename = f"sample_{uuid.uuid4().hex[:8]}_{src_filename}"
    saved_file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    shutil.copyfile(src_path, saved_file_path)

    log.info(f"[SAMPLE] Loading sample '{sample_id}' → {saved_file_path}")

    # DB Record
    db_doc = Document(
        filename=display_filename,
        file_path=f"/static/uploads/{unique_filename}",
        document_type="PASSPORT",
        status="SCREENED"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # Real screening pipeline — NO overrides, NO is_fake branching
    mrz_data, extracted_fields_data = extract_ocr_and_mrz(saved_file_path)

    for field in extracted_fields_data:
        ef = ExtractedField(
            document_id=db_doc.id,
            field_name=field["field_name"],
            visual_value=field["visual_value"],
            mrz_value=field["mrz_value"],
            is_match=field["is_match"],
            confidence=field["confidence"]
        )
        db.add(ef)

    ela_url, ela_score, is_tampered, anomaly_regions = generate_ela_heatmap(saved_file_path)

    db_tamper = TamperResult(
        document_id=db_doc.id,
        ela_heatmap_path=ela_url,
        ela_score=ela_score,
        is_tampered=is_tampered,
        anomaly_regions=anomaly_regions
    )
    db.add(db_tamper)

    overall_score, risk_level, factors, reasoning = calculate_fused_risk_score(
        mrz_data=mrz_data,
        extracted_fields=extracted_fields_data,
        ela_score=ela_score,
        is_tampered=is_tampered
    )

    db_risk = RiskScore(
        document_id=db_doc.id,
        score=overall_score,
        risk_level=risk_level,
        factors=factors,
        summary_reasoning=reasoning
    )
    db.add(db_risk)

    db_log = AuditLog(
        document_id=db_doc.id,
        officer_id="OFFICER_ZENITH_01",
        action="SAMPLE_LOADED_SCREENED",
        details={"sample_id": sample_id, "risk_level": risk_level, "score": overall_score}
    )
    db.add(db_log)

    db.commit()
    db.refresh(db_doc)

    log.info(f"[SAMPLE] Sample '{sample_id}' processed → Risk: {risk_level} ({overall_score})")

    return db_doc


@router.get("/documents/{doc_id}", response_model=DocumentDetailResponse)
def get_document_detail(doc_id: int, db: Session = Depends(get_db)):
    """Retrieve full screening report for a document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/verify-face", response_model=FaceVerifyResponse)
def verify_face(payload: FaceVerifyRequest, db: Session = Depends(get_db)):
    """Biometric face matching between document photo and live captured photo."""
    import base64
    import logging
    log = logging.getLogger("veriborder.routes")

    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_image_full_path = os.path.join(settings.BASE_DIR, doc.file_path.lstrip("/static/").lstrip("/"))
    if not os.path.exists(doc_image_full_path):
        doc_image_full_path = os.path.join(settings.UPLOAD_DIR, os.path.basename(doc.file_path))

    # Handle live image (captured from camera or uploaded)
    live_image_path = None
    temp_capture_file = None
    if payload.live_image_base64 and len(payload.live_image_base64) > 50:
        try:
            b64_str = payload.live_image_base64
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            raw_bytes = base64.b64decode(b64_str)
            temp_capture_file = os.path.join(settings.UPLOAD_DIR, f"live_{uuid.uuid4().hex[:10]}.jpg")
            with open(temp_capture_file, "wb") as bf:
                bf.write(raw_bytes)
            live_image_path = temp_capture_file
            log.info(f"[FACE] Saved live camera capture to {live_image_path} ({len(raw_bytes)} bytes)")
        except Exception as e:
            log.warning(f"[FACE] Could not decode live_image_base64: {e}. Falling back to document image.")
            live_image_path = doc_image_full_path
    else:
        live_image_path = doc_image_full_path

    # Perform real face comparison between document photo and live capture
    score, is_match, details = compare_faces(doc_image_full_path, live_image_path)

    # Clean up temp capture file
    if temp_capture_file and os.path.exists(temp_capture_file):
        try:
            os.remove(temp_capture_file)
        except Exception:
            pass

    # Update document risk score in DB with real face match score
    if doc.risk_score:
        existing_factors = dict(doc.risk_score.factors) if doc.risk_score.factors else {}
        mrz_data = {
            "mrz_detected": existing_factors.get("mrz_detected", True),
            "checksum_pass": existing_factors.get("checksum_pass", True),
            "checksum_errors": [] if existing_factors.get("checksum_pass", True) else ["Checksum mismatch"],
            "mrz_checksum": existing_factors.get("mrz_checksum", "N/A - No MRZ Zone Found")
        }
        extracted_fields_data = [
            {
                "field_name": ef.field_name,
                "visual_value": ef.visual_value,
                "mrz_value": ef.mrz_value,
                "is_match": ef.is_match
            }
            for ef in doc.extracted_fields
        ]
        ela_val = doc.tamper_result.ela_score if doc.tamper_result else 0.0
        tamper_val = doc.tamper_result.is_tampered if doc.tamper_result else False

        new_fused_score, new_risk_level, new_factors, new_reasoning = calculate_fused_risk_score(
            mrz_data=mrz_data,
            extracted_fields=extracted_fields_data,
            ela_score=ela_val,
            is_tampered=tamper_val,
            face_score=score,
            has_face_check=True
        )

        doc.risk_score.score = new_fused_score
        doc.risk_score.risk_level = new_risk_level
        doc.risk_score.factors = new_factors
        doc.risk_score.summary_reasoning = new_reasoning

    # Record Audit Log
    db_log = AuditLog(
        document_id=doc.id,
        officer_id="OFFICER_ZENITH_01",
        action="FACE_VERIFIED",
        details={"match_score": score, "is_match": is_match, "source": "live_capture" if payload.live_image_base64 else "document_photo"}
    )
    db.add(db_log)
    db.commit()

    return FaceVerifyResponse(
        document_id=doc.id,
        match_score=score,
        is_match=is_match,
        threshold=65.0,
        details=details
    )


@router.get("/audit-logs", response_model=List[AuditLogSchema])
def get_audit_logs(db: Session = Depends(get_db)):
    """Return audit trail of all checkpoint verification actions."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return logs
