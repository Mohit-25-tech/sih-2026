import os
import sys
import io
import cv2
import numpy as np
import logging
from typing import Tuple, Dict, Any

# Ensure standard output/error can handle utf-8 characters on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logger = logging.getLogger("veriborder.face_verification")

# ArcFace cosine distance cutoff recommended by DeepFace research
ARCFACE_COSINE_THRESHOLD = 0.68


def compare_faces(doc_image_path: str, live_image_path: str) -> Tuple[float, bool, str]:
    """
    Biometric Face Verification Engine using DeepFace with ArcFace model & MTCNN alignment.
    
    Pipeline:
    1. MTCNN face detector finds and tightly crops facial regions from BOTH document and live images.
    2. Aligns facial landmarks on eye coordinates (normalization against head tilt & scale).
    3. ArcFace deep neural network generates 512-dimensional face embeddings.
    4. Calculates cosine distance between the two face vectors.
    5. Evaluates against ArcFace's documented cosine threshold (0.68).
    6. Calibrates distance into a transparent 0-100% confidence/similarity score:
       - If distance <= 0.68 (verified): score = 70.0 + 29.0 * (1.0 - (distance / 0.68))  [70% - 99%]
       - If distance > 0.68 (mismatch): score = max(5.0, 70.0 * (1.0 - (distance - 0.68) / 0.32))  [5% - 69%]
    7. Logs raw bounding boxes and cosine distance to the backend console.
    8. If face detection fails on either image, explicitly returns 'Face not detected' with score 0.0.
    
    Returns: (match_score_0_to_100, is_match, explanation_details)
    """
    logger.info("═══════════════════════════════════════════════════════════════")
    logger.info("[FACE] ═══ Biometric Facial Verification Started ═══")
    logger.info(f"[FACE] Document image path : {doc_image_path}")
    logger.info(f"[FACE] Live image path     : {live_image_path}")

    if not os.path.exists(doc_image_path):
        logger.error(f"[FACE] Document image does not exist: {doc_image_path}")
        return 0.0, False, "Face not detected: Document image file not found on server."

    if not os.path.exists(live_image_path):
        logger.error(f"[FACE] Live capture image does not exist: {live_image_path}")
        return 0.0, False, "Face not detected: Live capture file not found on server."

    # Try primary deep learning pipeline: DeepFace with ArcFace + MTCNN
    backends_to_try = ["mtcnn", "retinaface"]
    
    last_error = ""
    for detector in backends_to_try:
        try:
            from deepface import DeepFace
            logger.info(f"[FACE] Running DeepFace.verify (model=ArcFace, detector={detector}, metric=cosine, align=True)...")
            
            result = DeepFace.verify(
                img1_path=doc_image_path,
                img2_path=live_image_path,
                model_name="ArcFace",
                detector_backend=detector,
                distance_metric="cosine",
                align=True,
                enforce_detection=True
            )

            distance = float(result.get("distance", 1.0))
            threshold = float(result.get("threshold", ARCFACE_COSINE_THRESHOLD))
            is_verified = bool(result.get("verified", distance <= threshold))
            facial_areas = result.get("facial_areas", {})
            doc_bbox = facial_areas.get("img1")
            live_bbox = facial_areas.get("img2")

            # Calibrate 0-100% confidence score using ArcFace threshold
            if distance <= threshold:
                # Verified same-person range: 70.0% to 99.0%
                ratio = max(0.0, min(1.0, distance / max(0.001, threshold)))
                calibrated_score = 70.0 + 29.0 * (1.0 - ratio)
            else:
                # Mismatch range: 5.0% to 69.9%
                excess = min(1.0, max(0.0, (distance - threshold) / max(0.001, (1.0 - threshold))))
                calibrated_score = max(5.0, 70.0 * (1.0 - excess))

            calibrated_score = round(calibrated_score, 1)

            # Strict logging of raw bounding boxes and embedding distance as requested
            logger.info(f"[FACE] Detector backend: {detector}")
            logger.info(f"[FACE] Document facial bounding box : {doc_bbox}")
            logger.info(f"[FACE] Live capture facial bounding box: {live_bbox}")
            logger.info(f"[FACE] Raw ArcFace cosine distance: {distance:.6f} (Threshold: {threshold:.2f})")
            logger.info(f"[FACE] Verification result: Verified={is_verified}, Calibrated Score={calibrated_score}%")
            logger.info("═══════════════════════════════════════════════════════════════")

            details_str = (
                f"ArcFace Deep Biometric Verification: "
                f"Cosine Distance={distance:.4f} (Cutoff={threshold:.2f}). "
                f"Confidence Score={calibrated_score}%."
            )

            return calibrated_score, is_verified, details_str

        except ValueError as val_err:
            err_msg = str(val_err)
            last_error = err_msg
            # Check if this was a face detection failure
            if "Face could not be detected" in err_msg or "enforce_detection" in err_msg:
                logger.warning(f"[FACE] Face detection failed with detector '{detector}': {err_msg}")
                # Try next detector in backends_to_try
                continue
            else:
                logger.warning(f"[FACE] DeepFace ValueError ({detector}): {err_msg}")
                continue
        except Exception as exc:
            err_msg = str(exc)
            last_error = err_msg
            logger.warning(f"[FACE] DeepFace exception with detector '{detector}': {exc}")
            continue

    # If all detectors failed with "Face could not be detected"
    if "Face could not be detected" in last_error or "enforce_detection" in last_error:
        logger.warning("[FACE] Face detection failed on one or both images across all detectors.")
        logger.info("═══════════════════════════════════════════════════════════════")
        return 0.0, False, "Face not detected: Could not locate a clear human face in document photo or live capture."

    # Fallback to OpenCV structural comparison if deep learning backend fails unexpectedly
    logger.warning(f"[FACE] Deep learning pipeline failed ({last_error}). Checking for facial presence.")
    return 0.0, False, f"Face not detected or verification error: {last_error}"
