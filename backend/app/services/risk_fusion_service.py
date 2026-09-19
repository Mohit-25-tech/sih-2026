import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("veriborder.risk_fusion")

def calculate_fused_risk_score(
    mrz_data: Dict[str, Any],
    extracted_fields: List[Dict[str, Any]],
    ela_score: float,
    is_tampered: bool,
    face_score: float = 90.0,
    has_face_check: bool = False
) -> Tuple[float, str, Dict[str, Any], str]:
    """
    Weighted Risk Fusion Engine:
    - MRZ Checksum Pass/Fail: 30%
    - Visual OCR vs MRZ Field Mismatch: 25%
    - ELA Tamper Confidence Score: 35%
    - Biometric Face Match Score: 10%
    
    Handles the case where no MRZ zone was detected (e.g. non-passport documents)
    by assigning moderate risk to the MRZ component.
    
    Returns (overall_score, risk_level, factors_dict, plain_language_reasoning)
    """
    mrz_detected = mrz_data.get("mrz_detected", True)
    
    logger.info(f"[RISK] ═══ Risk Fusion Calculation ═══")
    logger.info(f"[RISK] MRZ detected: {mrz_detected}")
    logger.info(f"[RISK] ELA score: {ela_score}, Is tampered: {is_tampered}")

    # 1. MRZ Checksum Score (0 = No Risk, 100 = High Risk)
    if not mrz_detected:
        # No MRZ zone found — moderate risk (cannot verify via standard checksum)
        mrz_risk_score = 50.0
        checksum_pass = False
        checksum_errors = mrz_data.get("checksum_errors", ["N/A — No MRZ Zone Found"])
    else:
        checksum_pass = mrz_data.get("checksum_pass", True)
        checksum_errors = mrz_data.get("checksum_errors", [])
        mrz_risk_score = 0.0 if checksum_pass else 100.0

    # 2. Field Mismatch Score
    mismatched_fields = [f for f in extracted_fields if not f.get("is_match", True)]
    total_fields = max(1, len(extracted_fields))
    
    if not mrz_detected:
        # If no MRZ detected, all fields show "Not Detected" — don't count those as mismatches
        # Only count fields where both visual and MRZ values exist but differ
        real_mismatches = [
            f for f in mismatched_fields 
            if f.get("visual_value", "") != "Not Detected" and f.get("mrz_value", "") != "Not Detected"
        ]
        mismatch_ratio = len(real_mismatches) / total_fields
    else:
        mismatch_ratio = len(mismatched_fields) / total_fields
    
    mismatch_risk_score = min(100.0, mismatch_ratio * 140.0)  # Heavy penalty per mismatch

    # 3. ELA Forensic Tamper Score
    ela_risk_score = min(100.0, max(0.0, ela_score))

    # 4. Biometric Face Score (Inverted: low match = high risk)
    face_risk_score = (100.0 - face_score) if has_face_check else 0.0

    # Weighted Sum Formula
    fused_score = (
        (mrz_risk_score * 0.30) +
        (mismatch_risk_score * 0.25) +
        (ela_risk_score * 0.35) +
        (face_risk_score * 0.10)
    )

    fused_score = round(min(100.0, max(0.0, fused_score)), 1)

    # Risk Level Categorization
    if fused_score < 30.0:
        risk_level = "LOW"
    elif fused_score < 65.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    logger.info(f"[RISK] Component scores: MRZ={mrz_risk_score}, Mismatch={mismatch_risk_score:.1f}, "
                f"ELA={ela_risk_score:.1f}, Face={face_risk_score:.1f}")
    logger.info(f"[RISK] Fused score: {fused_score} → Risk level: {risk_level}")

    # Factors Breakdown
    factors = {
        "mrz_checksum_score": round(mrz_risk_score, 1),
        "field_mismatch_score": round(mismatch_risk_score, 1),
        "ela_forensic_score": round(ela_risk_score, 1),
        "face_match_score": round(face_score, 1),
        "checksum_pass": checksum_pass,
        "mismatched_count": len(mismatched_fields),
        "mrz_detected": mrz_detected
    }

    # Generate Plain-Language Reasoning Summary
    reason_lines = []
    if risk_level == "HIGH":
        reason_lines.append(f"CRITICAL ALERTS DETECTED (Overall Risk: {fused_score}/100):")
    elif risk_level == "MEDIUM":
        reason_lines.append(f"MODERATE ANOMALIES FLAGGED (Overall Risk: {fused_score}/100):")
    else:
        reason_lines.append(f"DOCUMENT VERIFIED AUTHENTIC (Overall Risk: {fused_score}/100):")

    if not mrz_detected:
        reason_lines.append("• No MRZ zone present — document type not verifiable via standard ICAO 9303 checksum. This may indicate a non-standard document format (e.g., college ID, driver's license without MRZ).")
    elif not checksum_pass:
        err_msg = ", ".join(checksum_errors) if checksum_errors else "ICAO 9303 checksum digit invalid"
        reason_lines.append(f"• MRZ Cryptographic Checksum Failure: {err_msg}.")
    else:
        reason_lines.append("• MRZ Zone Checksum Digits (Document No, DOB, Expiry, Composite) verified valid.")

    if is_tampered or ela_score > 40.0:
        reason_lines.append(f"• ELA Heatmap Anomaly: High error level compression difference detected (ELA score {ela_score:.1f}%). Possible photo substitution or text overlay manipulation.")
    else:
        reason_lines.append(f"• Forensic ELA Analysis: Compression error levels within normal threshold ({ela_score:.1f}%). No digital manipulation detected.")

    if mismatched_fields:
        m_names = [f.get("field_name", "Field") for f in mismatched_fields]
        reason_lines.append(f"• Data Inconsistency: Mismatch between visual OCR text and MRZ zone in {len(mismatched_fields)} field(s) ({', '.join(m_names)}).")
    else:
        if mrz_detected:
            reason_lines.append("• Cross-Zone Validation: Visual OCR text matches parsed MRZ data 100%.")
        else:
            reason_lines.append("• Cross-Zone Validation: N/A — No MRZ zone available for comparison.")

    if has_face_check:
        if face_score >= 65.0:
            reason_lines.append(f"• Biometric Verification: Live face photo matches document photo ({face_score:.1f}% similarity).")
        else:
            reason_lines.append(f"• Biometric Flag: Facial mismatch between live subject and document photo ({face_score:.1f}% similarity).")

    summary_reasoning = "\n".join(reason_lines)

    logger.info(f"[RISK] ═══ Risk Fusion Complete ═══")

    return fused_score, risk_level, factors, summary_reasoning
