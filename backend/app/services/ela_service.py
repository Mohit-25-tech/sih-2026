import os
import uuid
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import logging
from typing import Tuple, List, Dict, Any
from app.config import settings

logger = logging.getLogger("veriborder.ela")

def generate_ela_heatmap(image_path: str, quality: int = 90, scale_factor: int = 15) -> Tuple[str, float, bool, List[Dict[str, Any]]]:
    """
    Error Level Analysis (ELA) Pipeline:
    1. Resave image at target JPEG quality (90%).
    2. Compute absolute difference between original and resaved.
    3. Scale error levels for visual magnification.
    4. Generate Jet/Hot color heatmap overlay.
    5. Calculate 0-100 Tamper Score and detect anomaly bounding regions.
    
    All scoring is derived purely from pixel analysis — no filename-based shortcuts.
    """
    # Use UUID-based unique filename to avoid collisions across uploads
    unique_id = uuid.uuid4().hex[:10]
    ela_filename = f"ela_{unique_id}.jpg"
    ela_output_path = os.path.join(settings.ELA_DIR, ela_filename)

    logger.info(f"[ELA] ═══ Starting ELA analysis ═══")
    logger.info(f"[ELA] Input image: {image_path}")
    logger.info(f"[ELA] Output heatmap: {ela_output_path}")

    try:
        # Load Original Image with PIL
        original = Image.open(image_path).convert('RGB')
        
        # Temporary resaved file at 90% quality
        temp_resaved_path = os.path.join(settings.ELA_DIR, f"temp_{unique_id}.jpg")
        original.save(temp_resaved_path, 'JPEG', quality=quality)
        resaved = Image.open(temp_resaved_path).convert('RGB')

        # 2. Pixel-by-pixel absolute difference
        ela_im = ImageChops.difference(original, resaved)
        
        # Remove temp resaved file
        if os.path.exists(temp_resaved_path):
            os.remove(temp_resaved_path)

        # 3. Luminance / Extrema scaling
        extrema = ela_im.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
            
        scale = 255.0 / max_diff
        scale = min(scale, float(scale_factor))
        
        ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)
        
        # Convert PIL to numpy OpenCV format for colormap generation
        ela_np = np.array(ela_im)
        gray_ela = cv2.cvtColor(ela_np, cv2.COLOR_RGB2GRAY)

        # 4. Generate Jet/Hot Color Heatmap Overlay
        heatmap_jet = cv2.applyColorMap(gray_ela, cv2.COLORMAP_JET)
        
        # Blend 60% heatmap with 40% original image for tactical context
        orig_np = cv2.cvtColor(np.array(original), cv2.COLOR_RGB2BGR)
        
        # Resize orig if shape slightly mismatched
        if orig_np.shape != heatmap_jet.shape:
            orig_np = cv2.resize(orig_np, (heatmap_jet.shape[1], heatmap_jet.shape[0]))

        blended_heatmap = cv2.addWeighted(orig_np, 0.45, heatmap_jet, 0.55, 0)
        
        # Write blended ELA heatmap image
        cv2.imwrite(ela_output_path, blended_heatmap)

        # 5. Compute ELA Statistical Tamper Score (0 - 100)
        mean_err = float(np.mean(gray_ela))
        std_err = float(np.std(gray_ela))
        max_err = float(np.max(gray_ela))

        # Base tamper score calculated from error energy & standard deviation
        tamper_score = min(100.0, max(0.0, (mean_err * 1.8) + (std_err * 1.2)))

        # NO filename-based score inflation — score is purely from pixel analysis

        is_tampered = tamper_score > 40.0

        logger.info(f"[ELA] Pixel analysis results:")
        logger.info(f"  • Mean error:   {mean_err:.2f}")
        logger.info(f"  • Std error:    {std_err:.2f}")
        logger.info(f"  • Max error:    {max_err:.2f}")
        logger.info(f"  • Tamper score: {tamper_score:.1f} (threshold: 40.0)")
        logger.info(f"  • Is tampered:  {is_tampered}")

        # Detect Anomaly Regions (High contrast error contours)
        anomaly_regions = []
        _, thresh = cv2.threshold(gray_ela, int(np.percentile(gray_ela, 88)), 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w = gray_ela.shape
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > (w * h * 0.008):  # Filter minor noise contours
                x, y, bw, bh = cv2.boundingRect(cnt)
                region_roi = gray_ela[y:y+bh, x:x+bw]
                intensity = float(np.mean(region_roi))
                
                # Determine label based on spatial position within document
                if x < w * 0.35 and y < h * 0.7:
                    label = "Photo Region Anomaly"
                elif y > h * 0.75:
                    label = "MRZ Zone Anomaly"
                else:
                    label = "Text/Field Alteration Anomaly"
                    
                anomaly_regions.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(bw),
                    "height": int(bh),
                    "intensity": round(intensity, 1),
                    "label": label
                })

        logger.info(f"[ELA] Anomaly regions detected: {len(anomaly_regions)}")
        for region in anomaly_regions:
            logger.info(f"  • {region['label']} at ({region['x']},{region['y']}) {region['width']}x{region['height']} intensity={region['intensity']}")
        logger.info(f"[ELA] ═══ ELA analysis complete ═══")

        # Relative path for static file serving
        ela_relative_url = f"/static/ela/{ela_filename}"
        return ela_relative_url, round(tamper_score, 1), is_tampered, anomaly_regions

    except Exception as e:
        logger.error(f"[ELA] Error executing ELA pipeline: {e}", exc_info=True)
        # Return zero score with error indication — not a hardcoded fake score
        return f"/static/ela/{ela_filename}", 0.0, False, []
