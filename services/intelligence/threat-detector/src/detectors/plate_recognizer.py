"""
License Plate Recognition Module for AI Security Lab v4.0

License plate detection and OCR using EasyOCR.
"""

import asyncio
import base64
import logging
from typing import List, Optional, Dict, Any
import numpy as np
import cv2
import io
from PIL import Image
import re

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class PlateRecognizer:
    """
    License plate detection and recognition using EasyOCR.
    """

    def __init__(self, languages: List[str] = None):
        self.reader = None
        self.is_initialized = False
        self.languages = languages or ['en']  # Default to English
        self.use_gpu = False  # Will be set during initialization

        # License plate patterns (US format, extend for other regions)
        self.plate_patterns = {
            'US': r'[A-Z0-9]{1,3}[\s\-]?[A-Z0-9]{3,4}',
            'US_FULL': r'[A-Z]{1,3}[\s\-]?[0-9]{1,4}',
            'GENERIC': r'[A-Z0-9]{5,8}'
        }

    async def initialize(self):
        """Initialize the license plate recognition model."""
        try:
            if not EASYOCR_AVAILABLE:
                logger.warning("⚠️  EasyOCR not available")
                logger.info("Install easyocr for license plate recognition: pip install easyocr")
                self.is_initialized = False
                return

            logger.info(f"Loading EasyOCR with languages: {self.languages}")

            # Check for GPU availability
            import torch
            self.use_gpu = torch.cuda.is_available()

            # Initialize EasyOCR reader
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.use_gpu,
                verbose=False
            )

            if self.use_gpu:
                logger.info(f"✅ EasyOCR initialized with GPU support")
            else:
                logger.info(f"✅ EasyOCR initialized (CPU mode)")

            self.is_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize license plate recognizer: {e}")
            self.is_initialized = False
            raise

    async def recognize_plate(
        self,
        frame_data: str,
        bbox: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Recognize license plates in an image frame.

        Args:
            frame_data: Base64 encoded image data
            bbox: Optional bounding box to focus recognition

        Returns:
            Dictionary with license plate recognition results
        """
        if not self.is_initialized:
            logger.warning("License plate recognizer not initialized")
            return {"plates": [], "count": 0}

        try:
            # Decode image
            image = self._decode_image(frame_data)
            if image is None:
                return {"plates": [], "count": 0}

            # Crop if bbox provided
            if bbox:
                x1, y1, x2, y2 = map(int, bbox)
                image = image[y1:y2, x1:x2]

            # Preprocess image for better OCR
            processed_image = self._preprocess_for_ocr(image)

            # Run OCR
            ocr_results = self.reader.readtext(processed_image)

            # Process results and filter for license plate patterns
            plates = []
            for (bbox_coords, text, confidence) in ocr_results:
                # Clean up text
                clean_text = self._clean_plate_text(text)

                # Check if it matches license plate pattern
                if self._is_likely_plate(clean_text):
                    plates.append({
                        "text": clean_text,
                        "raw_text": text,
                        "confidence": float(confidence),
                        "bbox": bbox_coords,
                        "pattern_match": self._get_pattern_match(clean_text)
                    })

            # Sort by confidence
            plates.sort(key=lambda x: x['confidence'], reverse=True)

            results = {
                "plates": plates,
                "count": len(plates),
                "model": "EasyOCR",
                "languages": self.languages
            }

            if plates:
                logger.debug(f"Detected {len(plates)} potential license plates")
                for plate in plates:
                    logger.debug(f"  - {plate['text']} (conf: {plate['confidence']:.3f})")

            return results

        except Exception as e:
            logger.error(f"License plate recognition failed: {e}")
            return {"plates": [], "count": 0, "error": str(e)}

    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy."""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            # Apply bilateral filter to reduce noise while keeping edges sharp
            denoised = cv2.bilateralFilter(gray, 11, 17, 17)

            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Apply morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            return morph

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image

    def _clean_plate_text(self, text: str) -> str:
        """Clean and normalize license plate text."""
        # Remove spaces and special characters
        cleaned = text.upper().strip()
        cleaned = cleaned.replace(' ', '').replace('-', '').replace('.', '')

        # Common OCR corrections for license plates
        corrections = {
            'O': '0',  # Letter O to number 0
            'I': '1',  # Letter I to number 1
            'Z': '2',  # Sometimes Z is misread as 2
            'S': '5',  # Sometimes S is misread as 5
            'B': '8',  # Sometimes B is misread as 8
        }

        # Apply corrections intelligently
        # (In a real system, you'd use more sophisticated logic)
        result = cleaned

        return result

    def _is_likely_plate(self, text: str) -> bool:
        """Check if text matches common license plate patterns."""
        if len(text) < 5 or len(text) > 10:
            return False

        # Check against known patterns
        for pattern_name, pattern in self.plate_patterns.items():
            if re.match(pattern, text):
                return True

        # Generic check: mix of letters and numbers
        has_letters = any(c.isalpha() for c in text)
        has_numbers = any(c.isdigit() for c in text)

        return has_letters and has_numbers

    def _get_pattern_match(self, text: str) -> Optional[str]:
        """Get which pattern the plate matches."""
        for pattern_name, pattern in self.plate_patterns.items():
            if re.match(pattern, text):
                return pattern_name
        return None

    def _decode_image(self, frame_data: str) -> Optional[np.ndarray]:
        """Decode base64 image data to numpy array."""
        try:
            # Remove data URL prefix if present
            if "," in frame_data:
                frame_data = frame_data.split(",")[1]

            # Decode base64
            image_bytes = base64.b64decode(frame_data)

            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Convert to numpy array
            image_array = np.array(pil_image)

            return image_array

        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None

    def add_custom_pattern(self, name: str, pattern: str):
        """Add a custom license plate pattern."""
        self.plate_patterns[name] = pattern
        logger.info(f"Added custom plate pattern: {name} = {pattern}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the license plate recognizer."""
        return {
            "model_type": "EasyOCR" if EASYOCR_AVAILABLE else "None",
            "easyocr_available": EASYOCR_AVAILABLE,
            "using_ml_model": self.is_initialized,
            "languages": self.languages,
            "using_gpu": self.use_gpu,
            "supported_patterns": list(self.plate_patterns.keys()),
            "is_initialized": self.is_initialized
        }
