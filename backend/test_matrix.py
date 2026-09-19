import os
import sys
import io

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from app.services.ocr_mrz_service import extract_ocr_and_mrz
from app.services.risk_fusion_service import calculate_fused_risk_score
from app.services.face_service import compare_faces
from app.services.ela_service import generate_ela_heatmap

print("================================================================================")
print("TEST 1: Genuine Passport Sample with Real MRZ Zone")
print("================================================================================")
passport_img = "static/samples/sample_authentic_passport.jpg"
mrz1, fields1 = extract_ocr_and_mrz(passport_img)
_, ela_score1, is_tampered1, _ = generate_ela_heatmap(passport_img)
score1, level1, factors1, reasoning1 = calculate_fused_risk_score(mrz1, fields1, ela_score1, is_tampered1)

print(f"MRZ Detected         : {factors1.get('mrz_detected')}")
print(f"MRZ Checksum         : {factors1.get('mrz_checksum')}")
print(f"Field Consistency    : {factors1.get('field_consistency_status')}")
print(f"ELA Score            : {ela_score1:.1f}%")
print(f"Face Match Score     : Not Run (—)")
print(f"Final Risk Score     : {score1}/100 ({level1})")
print("Field Comparison Sample:")
for f in fields1[:3]:
    print(f"  • {f['field_name']}: Visual='{f['visual_value']}' | MRZ='{f['mrz_value']}' | Match={f['is_match']}")
print("\nReasoning Summary:")
print(reasoning1)

print("\n================================================================================")
print("TEST 2: College ID (No MRZ Zone Present)")
print("================================================================================")
college_img = "static/uploads/doc_cc444bd3b3.jpg"
mrz2, fields2 = extract_ocr_and_mrz(college_img)
_, ela_score2, is_tampered2, _ = generate_ela_heatmap(college_img)
score2, level2, factors2, reasoning2 = calculate_fused_risk_score(mrz2, fields2, ela_score2, is_tampered2)

print(f"MRZ Detected         : {factors2.get('mrz_detected')}")
print(f"MRZ Checksum         : {factors2.get('mrz_checksum')}")
print(f"Field Consistency    : {factors2.get('field_consistency_status')}")
print(f"Mismatched Count     : {factors2.get('mismatched_count')}")
print(f"ELA Score            : {ela_score2:.1f}%")
print(f"Face Match Score     : Not Run (—)")
print(f"Final Risk Score     : {score2}/100 ({level2})")
print("\nReasoning Summary:")
print(reasoning2)

print("\n================================================================================")
print("TEST 3: Aadhaar Card (No MRZ) + Biometric Face Verification")
print("================================================================================")
aadhar_img = "static/uploads/doc_eb5d20ba8d.jpg"
mrz3, fields3 = extract_ocr_and_mrz(aadhar_img)
_, ela_score3, is_tampered3, _ = generate_ela_heatmap(aadhar_img)

# Face verification of Aadhaar photo against same person photo
print("\n[Running DeepFace ArcFace Biometric Face Verification...]")
face_score3, is_face_match3, face_details3 = compare_faces(aadhar_img, college_img)

score3, level3, factors3, reasoning3 = calculate_fused_risk_score(
    mrz_data=mrz3,
    extracted_fields=fields3,
    ela_score=ela_score3,
    is_tampered=is_tampered3,
    face_score=face_score3,
    has_face_check=True
)

print(f"\nMRZ Detected         : {factors3.get('mrz_detected')}")
print(f"MRZ Checksum         : {factors3.get('mrz_checksum')}")
print(f"Field Consistency    : {factors3.get('field_consistency_status')}")
print(f"ELA Score            : {ela_score3:.1f}%")
print(f"Face Match Score     : {face_score3}% (Verified={is_face_match3})")
print(f"Final Risk Score     : {score3}/100 ({level3})")
print(f"Biometric Details    : {face_details3}")
print("\nReasoning Summary:")
print(reasoning3)
print("================================================================================")
