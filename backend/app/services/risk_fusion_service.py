import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("veriborder.risk_fusion")

def calculate_fused_risk_score(
    mrz_data: Dict[str, Any],
    extracted_fields: List[Dict[str, Any]],
    ela_score: float,
    is_tampered: bool,
    face_score: float = None,
    has_face_check: bool = False
) -> Tuple[float, str, Dict[str, Any], str]:
    """
    Document-Type-Agnostic Risk Fusion Engine:
    
    Active check weighting policy:
    1. For MRZ Documents (Passports, Visas):
       - Without Face Check:
           - MRZ Cryptographic Checksum: 33.3% (30 / 90)
           - Cross-Zone Visual vs MRZ Mismatch: 27.8% (25 / 90)
           - Forensic ELA Compression Analysis: 38.9% (35 / 90)
       - With Face Check:
           - MRZ Cryptographic Checksum: 30%
           - Cross-Zone Visual vs MRZ Mismatch: 25%
           - Forensic ELA Compression Analysis: 35%
           - Biometric Facial Verification: 10%
           
    2. For Non-MRZ Documents (Aadhaar cards, College IDs, Driver's Licenses):
       - MRZ Checksum is N/A (0% weight, 0 penalty)
       - Cross-Zone Field Consistency is N/A (0% weight, 0 penalty)
       - Without Face Check:
           - Forensic ELA Compression Analysis: 100%
       - With Face Check:
           - Forensic ELA Compression Analysis: 85%
           - Biometric Facial Verification: 15%
           
    This guarantees non-MRZ documents are never penalized for lacking an MRZ zone.
    Checks returning N/A are completely excluded from the plain-language reasoning.
    """
    mrz_detected = bool(mrz_data.get("mrz_detected", False))
    
    logger.info(f"[RISK] ═══ Risk Fusion Calculation ═══")
    logger.info(f"[RISK] MRZ detected: {mrz_detected}")
    logger.info(f"[RISK] ELA score: {ela_score}, Is tampered: {is_tampered}")
    logger.info(f"[RISK] Face check run: {has_face_check}, Face score: {face_score}")

    # 1. MRZ Checksum Score (Active only if MRZ is detected)
    if mrz_detected:
        checksum_pass = bool(mrz_data.get("checksum_pass", True))
        checksum_errors = mrz_data.get("checksum_errors", [])
        mrz_risk_score = 0.0 if checksum_pass else 100.0
        mrz_checksum_status = "PASS" if checksum_pass else "FAIL"
    else:
        checksum_pass = None
        checksum_errors = []
        mrz_risk_score = 0.0
        mrz_checksum_status = "N/A"

    # 2. Field Mismatch Score (Active only if MRZ is detected)
    if mrz_detected:
        # A field can ONLY be classified as a mismatch if BOTH values were extracted
        real_mismatches = [
            f for f in extracted_fields
            if f.get("visual_value") and f.get("visual_value") != "Not Detected"
            and f.get("mrz_value") and f.get("mrz_value") != "Not Detected"
            and not f.get("is_match", True)
        ]
        total_compared = len([
            f for f in extracted_fields
            if f.get("visual_value") and f.get("visual_value") != "Not Detected"
            and f.get("mrz_value") and f.get("mrz_value") != "Not Detected"
        ])
        mismatch_ratio = (len(real_mismatches) / max(1, total_compared)) if total_compared > 0 else 0.0
        mismatch_risk_score = min(100.0, mismatch_ratio * 140.0)
        field_consistency_status = "Consistent" if len(real_mismatches) == 0 else f"{len(real_mismatches)} Mismatches"
        mismatched_count = len(real_mismatches)
    else:
        real_mismatches = []
        total_compared = 0
        mismatch_risk_score = 0.0
        field_consistency_status = "N/A"
        mismatched_count = 0

    # 3. ELA Forensic Tamper Score
    ela_risk_score = min(100.0, max(0.0, ela_score))

    # 4. Biometric Face Score
    face_risk_score = max(0.0, min(100.0, 100.0 - face_score)) if (has_face_check and face_score is not None) else 0.0

    # 5. Weighted Risk Fusion (Proportional across active checks only)
    if not mrz_detected:
        # Non-MRZ Document: Only ELA (and Face, if verified) are active checks
        if has_face_check and face_score is not None:
            fused_score = (ela_risk_score * 0.85) + (face_risk_score * 0.15)
        else:
            fused_score = ela_risk_score
    else:
        # MRZ Document: Full 4-factor or 3-factor proportional fusion
        if has_face_check and face_score is not None:
            fused_score = (
                (mrz_risk_score * 0.30) +
                (mismatch_risk_score * 0.25) +
                (ela_risk_score * 0.35) +
                (face_risk_score * 0.10)
            )
        else:
            fused_score = (
                (mrz_risk_score * (0.30 / 0.90)) +
                (mismatch_risk_score * (0.25 / 0.90)) +
                (ela_risk_score * (0.35 / 0.90))
            )

    fused_score = round(min(100.0, max(0.0, fused_score)), 1)

    # Risk Level Categorization
    if fused_score < 30.0:
        risk_level = "LOW"
    elif fused_score < 65.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    logger.info(f"[RISK] Component scores: MRZ={'N/A' if not mrz_detected else mrz_risk_score}, "
                f"Mismatch={'N/A' if not mrz_detected else round(mismatch_risk_score, 1)}, "
                f"ELA={ela_risk_score:.1f}, Face={'N/A' if not has_face_check else round(face_risk_score, 1)}")
    logger.info(f"[RISK] Fused score: {fused_score} → Risk level: {risk_level}")

    # Factors Breakdown
    factors = {
        "mrz_detected": mrz_detected,
        "mrz_checksum": mrz_checksum_status,
        "mrz_checksum_score": round(mrz_risk_score, 1) if mrz_detected else None,
        "checksum_pass": checksum_pass,
        "field_consistency_status": field_consistency_status,
        "field_mismatch_score": round(mismatch_risk_score, 1) if mrz_detected else None,
        "mismatched_count": mismatched_count,
        "ela_forensic_score": round(ela_risk_score, 1),
        "has_face_check": has_face_check,
        "face_match_score": round(face_score, 1) if (has_face_check and face_score is not None) else None
    }

    # Generate Plain-Language Reasoning Summary (Only active checks included)
    reason_lines = []
    if risk_level == "HIGH":
        reason_lines.append(f"CRITICAL ALERTS DETECTED (Overall Risk: {fused_score}/100):")
    elif risk_level == "MEDIUM":
        reason_lines.append(f"MODERATE ANOMALIES FLAGGED (Overall Risk: {fused_score}/100):")
    else:
        reason_lines.append(f"DOCUMENT VERIFIED AUTHENTIC (Overall Risk: {fused_score}/100):")

    # 1. MRZ Checksum Bullet (ONLY if MRZ was detected on document)
    if mrz_detected:
        if not checksum_pass:
            err_msg = ", ".join(checksum_errors) if checksum_errors else "ICAO 9303 checksum digit invalid"
            reason_lines.append(f"• MRZ Cryptographic Checksum Failure: {err_msg}.")
        else:
            reason_lines.append("• MRZ Zone Checksum Digits (Document No, DOB, Expiry, Composite) verified valid.")

    # 2. Forensic ELA Analysis Bullet (Always active)
    if is_tampered or ela_score > 40.0:
        reason_lines.append(f"• ELA Heatmap Anomaly: High error level compression difference detected (ELA score {ela_score:.1f}%). Possible photo substitution or text overlay manipulation.")
    else:
        reason_lines.append(f"• Forensic ELA Analysis: Compression error levels within normal threshold ({ela_score:.1f}%). No digital manipulation detected.")

    # 3. Cross-Zone Field Validation Bullet (ONLY if MRZ detected and fields compared)
    if mrz_detected and total_compared > 0:
        if real_mismatches:
            m_names = [f.get("field_name", "Field") for f in real_mismatches]
            reason_lines.append(f"• Data Inconsistency: Mismatch between visual OCR text and MRZ zone in {len(real_mismatches)} field(s) ({', '.join(m_names)}).")
        else:
            reason_lines.append("• Cross-Zone Validation: Visual OCR text matches parsed MRZ data 100%.")

    # 4. Biometric Face Verification Bullet (ONLY if face verification was actually run)
    if has_face_check and face_score is not None:
        if face_score >= 65.0:
            reason_lines.append(f"• Biometric Verification: Live subject photo matches document photo ({face_score:.1f}% similarity).")
        else:
            reason_lines.append(f"• Biometric Flag: Facial mismatch between live subject and document photo ({face_score:.1f}% similarity).")
    summary_reasoning = "\n".join(reason_lines)
    logger.info(f"[RISK] ═══ Risk Fusion Complete ═══")

    return fused_score, risk_level, factors, summary_reasoning
