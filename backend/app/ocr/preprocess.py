import io
from typing import List, Dict
import cv2
import fitz
import numpy as np
from PIL import Image


def pdf_to_images(pdf_bytes: bytes) -> List[np.ndarray]:
    """
    Converts PDF pages into RGB numpy images for OCR using PyMuPDF (Section 6).
    If bytes represent an image (JPEG, PNG, TIFF), directly decodes into numpy ndarray.
    """
    # Check if raw bytes are already an image (JPEG, PNG, TIFF)
    if pdf_bytes.startswith(b"\xff\xd8\xff") or pdf_bytes.startswith(b"\x89PNG") or pdf_bytes.startswith(b"II*") or pdf_bytes.startswith(b"MM*"):
        try:
            pil_img = Image.open(io.BytesIO(pdf_bytes)).convert("RGB")
            return [np.array(pil_img)]
        except Exception:
            pass

    # Process as PDF
    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, pixmap.n)
            # Ensure RGB format
            if pixmap.n == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif pixmap.n == 1:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            pages.append(image)
        document.close()
        if pages:
            return pages
    except Exception:
        pass

    # Fallback to PIL decode
    try:
        pil_img = Image.open(io.BytesIO(pdf_bytes)).convert("RGB")
        return [np.array(pil_img)]
    except Exception:
        # Return a blank 800x600 canvas if byte stream is plain text or unparsable
        blank = np.full((800, 600, 3), 255, dtype=np.uint8)
        return [blank]


def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Detects and corrects orientation skew for rotated documents (Section 29 Test 3).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
    # Invert and threshold to find text line orientation
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 50:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only deskew if rotation is significant (> 0.5 degrees and < 45 degrees)
    if abs(angle) > 0.5 and abs(angle) < 45:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    return image


def get_image_variants(image: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Generates multiple preprocessing variants for adaptive OCR selection (Section 8).
    Different variants maximize OCR accuracy across clean typed, noisy scanned,
    photocopied, or low-contrast deeds.
    """
    rgb = image.copy()
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY) if len(rgb.shape) == 3 else rgb

    # 1. Grayscale standard
    # 2. Denoised using fast non-local means (Section 7)
    try:
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    except Exception:
        denoised = gray

    # 3. Adaptive Gaussian thresholding (Section 7)
    try:
        adaptive_thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )
    except Exception:
        adaptive_thresh = gray

    # 4. Contrast Limited Adaptive Histogram Equalization (CLAHE)
    try:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(gray)
    except Exception:
        contrast_enhanced = gray

    return {
        "original": rgb,
        "grayscale": gray,
        "denoised": denoised,
        "adaptive_threshold": adaptive_thresh,
        "contrast_enhanced": contrast_enhanced,
    }
