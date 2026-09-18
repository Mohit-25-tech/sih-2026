# VeriBorder — AI-Based Fake Identity & Document Screening System

**Team:** Zenith | **Event:** Smart India Hackathon 2026 | **Problem Statement ID:** SIH26187  
**Theme:** Border Security & Smart Automation

VeriBorder is a full-stack automated identity and travel document verification web application built for border checkpoint officers. It uploads documents (passports, visas, national IDs), extracts data via OCR and standard ICAO 9303 MRZ parsing, validates checksums, detects digital forgery/photo substitution using Error Level Analysis (ELA) heatmaps, performs biometric face matching, fuses all signals into an explainable 0–100 Risk Score (`LOW`, `MEDIUM`, `HIGH`), and presents forensic evidence on an officer command dashboard.

---

## Technical Stack & Architecture

```
[ Frontend: React (Vite) + TailwindCSS + Recharts ]
                      │ (REST API / Axios)
                      ▼
[ Backend: FastAPI (Python 3.10) ]
  ├── 1. OCR & MRZ Parser (PassportEye + PaddleOCR/EasyOCR + 7-3-1 Weighting Fallback)
  ├── 2. ELA Tampering Detector (PIL/OpenCV JPEG 90% resave diff + Jet/Hot Heatmap Overlay)
  ├── 3. Biometric Face Verification (DeepFace + OpenCV Haar Cascade/Histogram Fallback)
  ├── 4. Risk Fusion Engine (MRZ 30% + Field Mismatch 25% + ELA 35% + Face 10%)
  └── 5. Database (Neon Serverless PostgreSQL via DATABASE_URL / SQLite Fallback)
```

---

## Key Features

1. **ICAO 9303 MRZ 7-3-1 Checksum Validator**: Validates Document Number, Date of Birth, Expiry Date, and Composite checksum digits.
2. **Error Level Analysis (ELA) Forensic Pipeline**: Calculates compression level differences, scales error luminance, overlays Jet/Hot colormaps, and identifies bounding box anomaly coordinates for photo substitution or text altering.
3. **Biometric Face Verification**: Compares document photo with live subject snapshot.
4. **Weighted Risk Fusion Engine**: Combines all verification signals into an explainable score with plain-language evidence reasoning.
5. **Neon PostgreSQL Persistence**: Connects to Neon serverless Postgres using SQLAlchemy ORM with automatic SQLite fallback for zero-configuration local execution.
6. **1-Click Hackathon Presets**: Pre-seeded with sample authentic and tampered passports for instant end-to-end testing out of the box.

---

## Quick Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt

# (Optional) Set your Neon PostgreSQL DATABASE_URL in .env
# If unset, backend automatically falls back to local SQLite database (veriborder.db)
cp .env.example .env

# Generate preset sample passport images
python generate_samples.py

# Run backend verification test suite
python test_verification.py

# Start FastAPI server (runs on http://localhost:8000)
python run.py
```

### 2. Frontend Setup (React)
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

---

## Database Configuration (Neon PostgreSQL)

To connect to your **Neon Serverless PostgreSQL** database:
1. Copy `backend/.env.example` to `backend/.env`.
2. Set the `DATABASE_URL` variable:
   ```env
   DATABASE_URL=postgresql://neondb_owner:YOUR_NEON_PASSWORD@ep-sample-neon.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Restart the backend server. Tables (`documents`, `extracted_fields`, `tamper_results`, `risk_scores`, `audit_logs`) will be automatically initialized.

---

## API Endpoints Summary

- `POST /api/documents/upload` — Upload document image, run OCR/MRZ/ELA pipeline, calculate risk score, return full report.
- `GET /api/documents/{id}` — Retrieve full forensic report and ELA heatmap URL for a document.
- `GET /api/documents` — List all past screenings for audit history log.
- `POST /api/verify-face` — Run face verification matching between document photo and live snapshot.
- `GET /api/documents/samples` — List preset authentic and tampered demo documents.
- `POST /api/documents/load-sample/{sample_id}` — Instantly process a pre-configured sample document for 1-click testing.

---

## Verification & Test Results

Run `python backend/test_verification.py` to execute:
1. **MRZ 7-3-1 Checksum Validator Test**: Verifies valid MRZ strings pass and tampered MRZ check digits fail.
2. **ELA Heatmap Generation Test**: Confirms ELA heatmap files are generated and saved to `backend/static/ela/`.
3. **Database Connectivity Test**: Verifies table auto-creation on Neon Postgres / SQLite engine.

---

## Future Work (Out of Scope for Initial Prototype)
- **Federated Adversarial Learning Loop**: Distributed GAN-based continuous model retraining across global checkpoint gateways without sharing raw PII data.
- **Cross-Checkpoint Identity Resolution Graph**: Graph database clustering of face embeddings to flag repeat identity fraud across multiple border entry points.
