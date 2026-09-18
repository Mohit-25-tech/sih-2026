import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal
from app.services.ocr_mrz_service import parse_mrz_lines
from app.services.ela_service import generate_ela_heatmap

def test_mrz_checksums():
    print("=" * 60)
    print("TEST 1: MRZ 7-3-1 Checksum Validator Execution")
    print("=" * 60)

    # Valid MRZ lines (Exact 7-3-1 ICAO check digits: DocNum check digit 2, DOB check digit 1, EXP check digit 2)
    valid_lines = [
        "P<INDSHARMA<<RAHUL<KUMAR<<<<<<<<<<<<<<<<<<<",
        "J8293041<2IND9205141M2910242<<<<<<<<<<<<<<<0"
    ]
    parsed_valid = parse_mrz_lines(valid_lines)
    print(f"Valid MRZ Pass Status: {parsed_valid['checksum_pass']}")
    print(f"Parsed Doc Number: {parsed_valid['document_number']}")
    print(f"Parsed DOB: {parsed_valid['dob']}")
    print(f"Errors: {parsed_valid['checksum_errors']}")

    # Deliberately invalid MRZ lines (Corrupted doc num check digit from '2' -> '9')
    invalid_lines = [
        "P<INDSHARMA<<RAHUL<KUMAR<<<<<<<<<<<<<<<<<<<",
        "J8293041<9IND9205141M2910242<<<<<<<<<<<<<<<0"
    ]
    parsed_invalid = parse_mrz_lines(invalid_lines)
    print(f"\nDeliberately Invalid MRZ Pass Status: {parsed_invalid['checksum_pass']}")
    print(f"Detected Checksum Failures: {parsed_invalid['checksum_errors']}")
    
    assert parsed_valid['checksum_pass'] == True, "Valid MRZ failed!"
    assert parsed_invalid['checksum_pass'] == False, "Invalid MRZ was wrongly passed!"
    print(">>> MRZ 7-3-1 Checksum Validator Verification SUCCESSFUL!\n")

def test_ela_heatmap():
    print("=" * 60)
    print("TEST 2: ELA Heatmap File Writing Verification")
    print("=" * 60)
    sample_path = os.path.join(os.path.dirname(__file__), "static", "samples", "sample_tampered_passport.jpg")
    
    ela_url, score, is_tampered, anomalies = generate_ela_heatmap(sample_path)
    ela_full_path = os.path.join(os.path.dirname(__file__), ela_url.lstrip("/"))
    
    print(f"ELA Output URL: {ela_url}")
    print(f"ELA Tamper Score: {score}% | Tampered Flag: {is_tampered}")
    print(f"Anomalies Contour Count: {len(anomalies)}")
    print(f"Target ELA File Path: {ela_full_path}")
    
    exists = os.path.exists(ela_full_path)
    print(f"File Exists on Disk: {exists}")
    assert exists, "ELA Heatmap file was not written to static/ela/!"
    print(">>> ELA Heatmap Generator Verification SUCCESSFUL!\n")

def test_database():
    print("=" * 60)
    print("TEST 3: Database Table Auto-Creation Verification")
    print("=" * 60)
    init_db()
    db = SessionLocal()
    try:
        from app.models import Document
        count = db.query(Document).count()
        print(f"Database connection active! Current documents count: {count}")
        print(">>> Database Auto-Creation Verification SUCCESSFUL!\n")
    finally:
        db.close()

if __name__ == "__main__":
    test_mrz_checksums()
    test_ela_heatmap()
    test_database()
    print("=" * 60)
    print("ALL BACKEND VERIFICATION TESTS PASSED CLEANLY!")
    print("=" * 60)
