#!/usr/bin/env python3
"""
Simple test script to verify AI models can be initialized.
This tests the YOLOv8, MediaPipe, and EasyOCR integrations.
"""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_models():
    """Test all AI model initializations."""

    logger.info("=" * 60)
    logger.info("AI Security Lab v4.0 - Model Verification Test")
    logger.info("=" * 60)

    results = {
        "weapon_detector": {"status": "pending", "error": None},
        "face_detector": {"status": "pending", "error": None},
        "plate_recognizer": {"status": "pending", "error": None}
    }

    # Test Weapon Detector (YOLOv8)
    logger.info("\n[1/3] Testing Weapon Detector (YOLOv8)...")
    try:
        from src.detectors.weapon_detector import WeaponDetector

        weapon_detector = WeaponDetector()
        await weapon_detector.initialize()

        model_info = weapon_detector.get_model_info()
        logger.info(f"  ✅ Weapon Detector initialized successfully")
        logger.info(f"     - Model: {model_info.get('model_type', 'Unknown')}")
        logger.info(f"     - Using ML: {model_info.get('using_ml_model', False)}")
        logger.info(f"     - YOLO Available: {model_info.get('yolo_available', False)}")
        logger.info(f"     - CUDA Available: {model_info.get('cuda_available', False)}")

        results["weapon_detector"]["status"] = "passed"
        results["weapon_detector"]["info"] = model_info

    except Exception as e:
        logger.error(f"  ❌ Weapon Detector failed: {e}")
        results["weapon_detector"]["status"] = "failed"
        results["weapon_detector"]["error"] = str(e)

    # Test Face Detector (MediaPipe/InsightFace)
    logger.info("\n[2/3] Testing Face Detector (MediaPipe/InsightFace)...")
    try:
        from src.detectors.face_detector import FaceDetector

        face_detector = FaceDetector()
        await face_detector.initialize()

        model_info = face_detector.get_model_info()
        logger.info(f"  ✅ Face Detector initialized successfully")
        logger.info(f"     - Model: {model_info.get('model_type', 'Unknown')}")
        logger.info(f"     - Using ML: {model_info.get('using_ml_model', False)}")
        logger.info(f"     - MediaPipe Available: {model_info.get('mediapipe_available', False)}")
        logger.info(f"     - InsightFace Available: {model_info.get('insightface_available', False)}")

        results["face_detector"]["status"] = "passed"
        results["face_detector"]["info"] = model_info

    except Exception as e:
        logger.error(f"  ❌ Face Detector failed: {e}")
        results["face_detector"]["status"] = "failed"
        results["face_detector"]["error"] = str(e)

    # Test Plate Recognizer (EasyOCR)
    logger.info("\n[3/3] Testing Plate Recognizer (EasyOCR)...")
    try:
        from src.detectors.plate_recognizer import PlateRecognizer

        plate_recognizer = PlateRecognizer()
        await plate_recognizer.initialize()

        model_info = plate_recognizer.get_model_info()
        logger.info(f"  ✅ Plate Recognizer initialized successfully")
        logger.info(f"     - Model: {model_info.get('model_type', 'Unknown')}")
        logger.info(f"     - Using ML: {model_info.get('using_ml_model', False)}")
        logger.info(f"     - EasyOCR Available: {model_info.get('easyocr_available', False)}")
        logger.info(f"     - Using GPU: {model_info.get('using_gpu', False)}")

        results["plate_recognizer"]["status"] = "passed"
        results["plate_recognizer"]["info"] = model_info

    except Exception as e:
        logger.error(f"  ❌ Plate Recognizer failed: {e}")
        results["plate_recognizer"]["status"] = "failed"
        results["plate_recognizer"]["error"] = str(e)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary:")
    logger.info("=" * 60)

    passed = sum(1 for r in results.values() if r["status"] == "passed")
    failed = sum(1 for r in results.values() if r["status"] == "failed")

    for name, result in results.items():
        status_icon = "✅" if result["status"] == "passed" else "❌"
        logger.info(f"{status_icon} {name}: {result['status'].upper()}")
        if result["error"]:
            logger.info(f"   Error: {result['error']}")

    logger.info(f"\nPassed: {passed}/3")
    logger.info(f"Failed: {failed}/3")

    if failed == 0:
        logger.info("\n🎉 All AI models initialized successfully!")
        logger.info("The 7-factor threat analysis system is ready for production.")
        return 0
    else:
        logger.warning(f"\n⚠️  {failed} model(s) failed initialization")
        logger.warning("Check the errors above and install missing dependencies if needed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_models())
    sys.exit(exit_code)
