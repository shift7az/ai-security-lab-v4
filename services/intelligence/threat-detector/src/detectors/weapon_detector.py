"""
Weapon Detection Module for AI Security Lab v4.0

Computer vision module for detecting weapons in images and video frames using YOLOv8.
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image
import cv2
import io

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics not available, using heuristic-based detection")

logger = logging.getLogger(__name__)


class WeaponDetector:
    """
    Advanced weapon detection using YOLOv8 and computer vision.
    Falls back to heuristic-based detection if models are unavailable.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.use_yolo = YOLO_AVAILABLE
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = 0.5
        self.is_initialized = False
        self.model_path = model_path or "yolov8n.pt"  # Default to YOLOv8 nano

        # Weapon classes that we can detect
        self.weapon_classes = [
            'gun', 'rifle', 'pistol', 'knife', 'sword', 'bat', 'club',
            'grenade', 'bomb', 'explosive', 'weapon', 'firearm'
        ]

        # COCO classes that might be relevant for threat detection
        self.threat_objects = {
            'knife': 1.0,
            'baseball bat': 0.7,
            'bottle': 0.3,  # Potential weapon
            'scissors': 0.6
        }

        # Image preprocessing transforms (for heuristic mode)
        self.transforms = T.Compose([
            T.Resize((640, 640)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    async def initialize(self):
        """Initialize the weapon detection model."""
        try:
            if self.use_yolo:
                logger.info(f"Loading YOLOv8 model: {self.model_path}")

                # Check if custom weapon model exists
                custom_model_path = Path("/models") / "weapon_detection.pt"
                if custom_model_path.exists():
                    self.model_path = str(custom_model_path)
                    logger.info(f"Found custom weapon model: {self.model_path}")

                # Load YOLO model (will auto-download if not present)
                self.model = YOLO(self.model_path)

                # Move model to appropriate device
                if torch.cuda.is_available():
                    logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
                else:
                    logger.info("Using CPU for inference")

                logger.info(f"✅ YOLOv8 model loaded successfully")

            else:
                logger.warning("⚠️  YOLO not available, using heuristic-based detection")
                logger.info("Install ultralytics for ML-based weapon detection: pip install ultralytics")

            self.is_initialized = True
            logger.info("✅ Weapon detector ready")

        except Exception as e:
            logger.error(f"Failed to initialize weapon detector: {e}")
            logger.warning("Falling back to heuristic-based detection")
            self.use_yolo = False
            self.is_initialized = True  # Still mark as initialized but with fallback

    async def detect_weapon(
        self,
        frame_data: str,
        bbox: Optional[List[float]] = None
    ) -> float:
        """
        Detect weapons in an image frame.

        Args:
            frame_data: Base64 encoded image data
            bbox: Optional bounding box [x1, y1, x2, y2] to focus detection

        Returns:
            Weapon detection confidence score (0.0 to 1.0)
        """
        if not self.is_initialized:
            logger.warning("Weapon detector not initialized")
            return 0.0

        try:
            # Decode base64 image
            image = self._decode_image(frame_data)

            if image is None:
                return 0.0

            # If bbox provided, crop to region of interest
            if bbox:
                x1, y1, x2, y2 = map(int, bbox)
                image = image[y1:y2, x1:x2]

            # Run weapon detection
            weapon_score = await self._detect_weapons_in_image(image)

            return min(weapon_score, 1.0)

        except Exception as e:
            logger.error(f"Weapon detection failed: {e}")
            return 0.0

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

    async def _detect_weapons_in_image(self, image: np.ndarray) -> float:
        """
        Run weapon detection on image array.

        Args:
            image: Input image as numpy array

        Returns:
            Maximum weapon detection confidence
        """
        try:
            if self.use_yolo and self.model is not None:
                # Use YOLOv8 for detection
                return await self._yolo_detection(image)
            else:
                # Fall back to heuristic-based detection
                return await self._heuristic_detection(image)

        except Exception as e:
            logger.error(f"Weapon detection analysis failed: {e}")
            return 0.0

    async def _yolo_detection(self, image: np.ndarray) -> float:
        """
        Run YOLOv8-based weapon detection.

        Args:
            image: Input image as numpy array

        Returns:
            Maximum weapon detection confidence
        """
        try:
            # Run inference
            results = self.model(image, conf=self.confidence_threshold, verbose=False)

            max_confidence = 0.0

            # Process results
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # Get class name and confidence
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        cls_name = result.names[cls_id].lower()

                        # Check if it's a weapon class
                        is_weapon = False
                        weapon_multiplier = 1.0

                        # Direct weapon match
                        if any(weapon in cls_name for weapon in self.weapon_classes):
                            is_weapon = True
                            weapon_multiplier = 1.0

                        # Threat object match (from COCO)
                        elif cls_name in self.threat_objects:
                            is_weapon = True
                            weapon_multiplier = self.threat_objects[cls_name]

                        if is_weapon:
                            adjusted_conf = conf * weapon_multiplier
                            max_confidence = max(max_confidence, adjusted_conf)
                            logger.debug(f"Detected potential weapon: {cls_name} (conf: {conf:.3f}, adjusted: {adjusted_conf:.3f})")

            return max_confidence

        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            return 0.0

    async def _heuristic_detection(self, image: np.ndarray) -> float:
        """
        Fallback heuristic-based weapon detection.

        Args:
            image: Input image as numpy array

        Returns:
            Estimated weapon detection confidence
        """
        try:
            weapon_score = 0.0

            # Heuristic 1: Shape analysis (looking for long, thin objects)
            shape_score = self._analyze_weapon_shapes(image)
            weapon_score = max(weapon_score, shape_score)

            # Heuristic 2: Color analysis (looking for metallic/dark objects)
            color_score = self._analyze_weapon_colors(image)
            weapon_score = max(weapon_score, color_score)

            # Heuristic 3: Edge analysis (looking for sharp edges)
            edge_score = self._analyze_weapon_edges(image)
            weapon_score = max(weapon_score, edge_score)

            # Heuristic 4: Object detection (basic blob detection)
            blob_score = self._analyze_weapon_blobs(image)
            weapon_score = max(weapon_score, blob_score)

            return weapon_score

        except Exception as e:
            logger.error(f"Heuristic detection failed: {e}")
            return 0.0

    def _analyze_weapon_shapes(self, image: np.ndarray) -> float:
        """Analyze image for weapon-like shapes."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            max_aspect_ratio = 0.0

            for contour in contours:
                if len(contour) < 4:
                    continue

                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)

                # Skip very small objects
                if w < 10 or h < 10:
                    continue

                # Calculate aspect ratio
                aspect_ratio = max(w, h) / min(w, h)

                # Look for long, thin objects (potential weapons)
                if aspect_ratio > 3.0 and min(w, h) > 20:
                    max_aspect_ratio = max(max_aspect_ratio, aspect_ratio)

            # Convert aspect ratio to confidence score
            # Higher aspect ratios suggest more weapon-like shapes
            shape_score = min(max_aspect_ratio / 10.0, 1.0)

            return shape_score

        except Exception as e:
            logger.error(f"Shape analysis failed: {e}")
            return 0.0

    def _analyze_weapon_colors(self, image: np.ndarray) -> float:
        """Analyze image for weapon-like colors (metallic, dark)."""
        try:
            # Define color ranges for potential weapons
            # Dark colors (black guns, knives)
            dark_mask = np.all(image < 60, axis=-1)

            # Metallic colors (silver guns, blades)
            metallic_mask = (
                (image[:,:,0] > 150) & (image[:,:,1] > 150) & (image[:,:,2] > 150)
            )

            # Brown/tan colors (wooden stocks, handles)
            brown_mask = (
                (image[:,:,0] > 100) & (image[:,:,0] < 200) &
                (image[:,:,1] > 50) & (image[:,:,1] < 150) &
                (image[:,:,2] < 100)
            )

            # Calculate percentage of weapon-like colors
            total_pixels = image.shape[0] * image.shape[1]
            dark_pixels = np.sum(dark_mask)
            metallic_pixels = np.sum(metallic_mask)
            brown_pixels = np.sum(brown_mask)

            weapon_color_pixels = dark_pixels + metallic_pixels + brown_pixels
            color_percentage = weapon_color_pixels / total_pixels

            # Convert to confidence score
            color_score = min(color_percentage * 5.0, 1.0)  # Scale up the percentage

            return color_score

        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            return 0.0

    def _analyze_weapon_edges(self, image: np.ndarray) -> float:
        """Analyze image for sharp edges typical of weapons."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply multiple edge detection techniques
            edges_canny = cv2.Canny(gray, 50, 150)
            edges_sobel = np.sqrt(cv2.Sobel(gray, cv2.CV_64F, 1, 0)**2 +
                                cv2.Sobel(gray, cv2.CV_64F, 0, 1)**2)

            # Calculate edge density
            canny_density = np.sum(edges_canny > 0) / (image.shape[0] * image.shape[1])
            sobel_density = np.mean(edges_sobel) / 255.0

            # Combine edge metrics
            edge_score = (canny_density + sobel_density) / 2.0

            # Weapons typically have higher edge density than regular objects
            return min(edge_score * 3.0, 1.0)

        except Exception as e:
            logger.error(f"Edge analysis failed: {e}")
            return 0.0

    def _analyze_weapon_blobs(self, image: np.ndarray) -> float:
        """Analyze image for weapon-like blob patterns."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply threshold to find dark regions
            _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

            # Find contours (potential weapon blobs)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            weapon_like_blobs = 0

            for contour in contours:
                area = cv2.contourArea(contour)

                # Skip very small or very large blobs
                if area < 100 or area > 10000:
                    continue

                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)

                # Calculate aspect ratio
                aspect_ratio = max(w, h) / min(w, h)

                # Look for elongated shapes (potential weapons)
                if 2.0 < aspect_ratio < 10.0:
                    weapon_like_blobs += 1

            # Convert blob count to confidence score
            # More weapon-like blobs = higher confidence
            blob_score = min(weapon_like_blobs * 0.3, 1.0)

            return blob_score

        except Exception as e:
            logger.error(f"Blob analysis failed: {e}")
            return 0.0

    def get_detection_zones(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Get detailed detection zones for weapons in image.

        Returns:
            List of detection zones with confidence scores
        """
        try:
            # This would use the actual model for detailed detection
            # For now, return mock detection zones

            height, width = image.shape[:2]

            # Mock detection zones (in production, these would come from the model)
            detection_zones = [
                {
                    "bbox": [width // 4, height // 4, width // 2, height // 2],
                    "confidence": 0.7,
                    "weapon_type": "gun",
                    "zone_id": "zone_1"
                },
                {
                    "bbox": [width // 2, height // 2, width * 3 // 4, height * 3 // 4],
                    "confidence": 0.5,
                    "weapon_type": "knife",
                    "zone_id": "zone_2"
                }
            ]

            return detection_zones

        except Exception as e:
            logger.error(f"Failed to get detection zones: {e}")
            return []

    def is_weapon_detected(self, confidence: float) -> bool:
        """Check if weapon detection confidence indicates a weapon."""
        return confidence > self.confidence_threshold

    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for weapon detection."""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Weapon detection threshold set to {threshold}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the weapon detection model."""
        return {
            "model_type": "YOLOv8" if (self.use_yolo and self.model) else "Heuristic",
            "model_path": self.model_path if self.use_yolo else None,
            "yolo_available": YOLO_AVAILABLE,
            "using_ml_model": self.use_yolo and self.model is not None,
            "weapon_classes": self.weapon_classes,
            "threat_objects": list(self.threat_objects.keys()),
            "confidence_threshold": self.confidence_threshold,
            "device": str(self.device),
            "cuda_available": torch.cuda.is_available(),
            "is_initialized": self.is_initialized
        }
