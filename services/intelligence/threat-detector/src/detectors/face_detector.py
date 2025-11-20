"""
Face Detection Module for AI Security Lab v4.0

Face detection and recognition using MediaPipe and InsightFace.
"""

import asyncio
import base64
import logging
from typing import List, Optional, Dict, Any
import numpy as np
import cv2
import io
from PIL import Image

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Face detection and analysis using MediaPipe/InsightFace.
    """

    def __init__(self, use_insightface: bool = False):
        self.face_detector = None
        self.use_insightface = use_insightface and INSIGHTFACE_AVAILABLE
        self.use_mediapipe = MEDIAPIPE_AVAILABLE
        self.is_initialized = False
        self.min_detection_confidence = 0.5

    async def initialize(self):
        """Initialize the face detection model."""
        try:
            if self.use_insightface:
                logger.info("Loading InsightFace for face recognition...")
                self.face_detector = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
                self.face_detector.prepare(ctx_id=0, det_size=(640, 640))
                logger.info("✅ InsightFace initialized")

            elif self.use_mediapipe:
                logger.info("Loading MediaPipe Face Detection...")
                mp_face_detection = mp.solutions.face_detection
                self.face_detector = mp_face_detection.FaceDetection(
                    model_selection=1,  # 0=short range, 1=full range
                    min_detection_confidence=self.min_detection_confidence
                )
                logger.info("✅ MediaPipe Face Detection initialized")

            else:
                logger.warning("⚠️  No face detection library available")
                logger.info("Install mediapipe or insightface for face detection")

            self.is_initialized = True
            logger.info("✅ Face detector ready")

        except Exception as e:
            logger.error(f"Failed to initialize face detector: {e}")
            self.is_initialized = False
            raise

    async def detect_faces(
        self,
        frame_data: str,
        bbox: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Detect faces in an image frame.

        Args:
            frame_data: Base64 encoded image data
            bbox: Optional bounding box to focus detection

        Returns:
            Dictionary with face detection results
        """
        if not self.is_initialized:
            logger.warning("Face detector not initialized")
            return {"faces": [], "count": 0}

        try:
            # Decode image
            image = self._decode_image(frame_data)
            if image is None:
                return {"faces": [], "count": 0}

            # Crop if bbox provided
            if bbox:
                x1, y1, x2, y2 = map(int, bbox)
                image = image[y1:y2, x1:x2]

            # Run detection
            if self.use_insightface:
                results = await self._detect_with_insightface(image)
            elif self.use_mediapipe:
                results = await self._detect_with_mediapipe(image)
            else:
                results = {"faces": [], "count": 0}

            return results

        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {"faces": [], "count": 0, "error": str(e)}

    async def _detect_with_insightface(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect faces using InsightFace."""
        try:
            # Run detection and recognition
            faces = self.face_detector.get(image)

            results = {
                "faces": [],
                "count": len(faces),
                "model": "InsightFace"
            }

            for face in faces:
                face_info = {
                    "bbox": face.bbox.tolist(),
                    "confidence": float(face.det_score),
                    "landmarks": face.kps.tolist() if hasattr(face, 'kps') else None,
                    "embedding": face.embedding.tolist() if hasattr(face, 'embedding') else None,
                    "age": int(face.age) if hasattr(face, 'age') else None,
                    "gender": face.gender if hasattr(face, 'gender') else None,
                }
                results["faces"].append(face_info)

            return results

        except Exception as e:
            logger.error(f"InsightFace detection failed: {e}")
            return {"faces": [], "count": 0, "error": str(e)}

    async def _detect_with_mediapipe(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect faces using MediaPipe."""
        try:
            # MediaPipe expects RGB
            if len(image.shape) == 2:  # Grayscale
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:  # RGBA
                image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif image.shape[2] == 3:
                # Check if BGR or RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image

            # Run detection
            detection_results = self.face_detector.process(image_rgb)

            results = {
                "faces": [],
                "count": 0,
                "model": "MediaPipe"
            }

            if detection_results.detections:
                results["count"] = len(detection_results.detections)

                for detection in detection_results.detections:
                    # Get bounding box
                    bbox = detection.location_data.relative_bounding_box
                    h, w = image_rgb.shape[:2]

                    face_info = {
                        "bbox": [
                            int(bbox.xmin * w),
                            int(bbox.ymin * h),
                            int((bbox.xmin + bbox.width) * w),
                            int((bbox.ymin + bbox.height) * h)
                        ],
                        "confidence": float(detection.score[0]),
                        "landmarks": self._extract_landmarks(detection, w, h)
                    }
                    results["faces"].append(face_info)

            return results

        except Exception as e:
            logger.error(f"MediaPipe detection failed: {e}")
            return {"faces": [], "count": 0, "error": str(e)}

    def _extract_landmarks(self, detection, width: int, height: int) -> List[Dict[str, float]]:
        """Extract facial landmarks from MediaPipe detection."""
        landmarks = []
        if detection.location_data.relative_keypoints:
            for keypoint in detection.location_data.relative_keypoints:
                landmarks.append({
                    "x": keypoint.x * width,
                    "y": keypoint.y * height
                })
        return landmarks

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

            # Convert to numpy array (OpenCV format)
            image_array = np.array(pil_image)

            return image_array

        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the face detection model."""
        return {
            "model_type": "InsightFace" if self.use_insightface else ("MediaPipe" if self.use_mediapipe else "None"),
            "insightface_available": INSIGHTFACE_AVAILABLE,
            "mediapipe_available": MEDIAPIPE_AVAILABLE,
            "using_ml_model": self.use_insightface or self.use_mediapipe,
            "min_detection_confidence": self.min_detection_confidence,
            "is_initialized": self.is_initialized,
            "capabilities": {
                "detection": True,
                "recognition": self.use_insightface,
                "age_gender": self.use_insightface,
                "embeddings": self.use_insightface
            }
        }

    async def cleanup(self):
        """Cleanup resources."""
        if self.face_detector and self.use_mediapipe:
            self.face_detector.close()
        self.is_initialized = False
        logger.info("Face detector cleaned up")
