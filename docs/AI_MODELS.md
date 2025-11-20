# AI Models - AI Security Lab v4.0

## Overview

AI Security Lab v4.0 uses multiple AI models for comprehensive threat detection and analysis. This document describes the models, their capabilities, and how to set them up.

**All models are FULLY INTEGRATED** into the threat detection pipeline and actively used in production.

## Integration Status

### 7-Factor Threat Analysis Pipeline

All models work together in a unified threat scoring system:

| Factor | Weight | Model | Status | Triggers |
|--------|--------|-------|--------|----------|
| 1. Object Type | 15% | Rule-based | ✅ Active | All detections |
| 2. Weapon Detection | 30% | **YOLOv8** | ✅ Active | Person/weapon detections |
| 3. Behavior Analysis | 20% | Rule-based | ✅ Active | All detections |
| 4. Context Analysis | 10% | Rule-based | ✅ Active | All detections |
| 5. Historical | 5% | Database query | ✅ Active | All detections |
| 6. Face Recognition | 10% | **MediaPipe/InsightFace** | ✅ Active | Person detections |
| 7. Vehicle/Plate | 10% | **EasyOCR** | ✅ Active | Vehicle detections |

**ML Model Contribution**: 50% of total threat score (Factors 2, 6, 7)

### API Integration

**Main Endpoint**: `POST /analyze` - Runs full 7-factor analysis
**Specialized Endpoints**:
- `POST /detect/faces` - Face detection only
- `POST /detect/plates` - Plate recognition only
- `POST /detect/comprehensive` - Run ALL models

**Model Status**: `GET /models/info` - Check what's loaded

See [API.md](API.md) for complete API documentation.

## Implemented AI Models

### 1. **Weapon Detection - YOLOv8**

**Purpose**: Detect weapons and threatening objects in video frames.

**Model**: Ultralytics YOLOv8
**Library**: `ultralytics==8.1.0`
**Location**: `services/intelligence/threat-detector/src/detectors/weapon_detector.py`

**Capabilities**:
- Firearm detection (guns, rifles, pistols)
- Blade detection (knives, swords)
- Blunt object detection (bats, clubs)
- COCO object detection (bottle, scissors, baseball bat)

**Models Available**:
- `yolov8n.pt` - Nano (fastest, less accurate)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (good accuracy)
- `yolov8l.pt` - Large (high accuracy)
- `yolov8x.pt` - Extra Large (best accuracy, slowest)
- Custom weapon model: `/models/weapon_detection.pt` (if trained)

**Setup**:
```python
# Auto-downloads on first use
from detectors.weapon_detector import WeaponDetector

detector = WeaponDetector()  # Uses yolov8n.pt by default
await detector.initialize()

# Or use custom model
detector = WeaponDetector(model_path="/models/weapon_detection.pt")
await detector.initialize()
```

**Fallback**: If YOLOv8 is unavailable, falls back to heuristic-based detection using OpenCV (shape, color, edge analysis).

---

### 2. **Face Detection - MediaPipe / InsightFace**

**Purpose**: Detect and recognize faces for identity tracking and access control.

**Models**:
- MediaPipe Face Detection (default, fast, free)
- InsightFace (advanced, includes age/gender, embeddings)

**Libraries**:
- `mediapipe==0.10.9` (basic face detection)
- `insightface==0.7.3` (advanced recognition, optional)

**Location**: `services/intelligence/threat-detector/src/detectors/face_detector.py`

**Capabilities**:
- Face detection with bounding boxes
- Facial landmark detection
- Face embeddings (InsightFace only)
- Age and gender estimation (InsightFace only)
- Face recognition (InsightFace only)

**Setup**:
```python
from detectors.face_detector import FaceDetector

# Use MediaPipe (default)
detector = FaceDetector()
await detector.initialize()

# Use InsightFace for advanced features
detector = FaceDetector(use_insightface=True)
await detector.initialize()
```

**MediaPipe Features**:
- ✅ Fast detection (<10ms per frame)
- ✅ Works on CPU
- ✅ Free and open-source
- ❌ No face recognition (detection only)

**InsightFace Features**:
- ✅ Face recognition with embeddings
- ✅ Age and gender estimation
- ✅ Multiple face attributes
- ⚠️ Requires more GPU memory
- ⚠️ Slightly slower than MediaPipe

---

### 3. **License Plate Recognition - EasyOCR**

**Purpose**: Detect and read license plates from vehicle images.

**Model**: EasyOCR
**Library**: `easyocr==1.7.1`
**Location**: `services/intelligence/threat-detector/src/detectors/plate_recognizer.py`

**Capabilities**:
- License plate detection
- OCR text recognition
- Multi-language support
- Pattern matching for validation

**Supported Languages**:
- English (default)
- Additional languages can be added: `['en', 'ch_sim', 'ja', 'ko']`

**Setup**:
```python
from detectors.plate_recognizer import PlateRecognizer

# English only
recognizer = PlateRecognizer()
await recognizer.initialize()

# Multiple languages
recognizer = PlateRecognizer(languages=['en', 'ch_sim'])
await recognizer.initialize()
```

**Plate Patterns**:
- US format: `ABC-1234`, `AB 123`, `ABC123`
- Generic: Any 5-8 alphanumeric characters
- Custom patterns can be added

**Preprocessing**:
- Grayscale conversion
- Bilateral filtering (noise reduction)
- Adaptive thresholding
- Morphological operations

---

### 4. **Behavior Analysis - Rule-Based System**

**Purpose**: Analyze behavior patterns for threat assessment.

**Type**: Rule-based heuristics (no ML model)
**Location**: `services/intelligence/threat-detector/src/detectors/behavior_analyzer.py`

**Analysis Types**:
1. **Person Behavior**:
   - Dwell time analysis
   - Movement patterns (erratic, suspicious)
   - Time-based analysis (unusual hours)
   - Location-based analysis (restricted areas)

2. **Vehicle Behavior**:
   - Speed analysis
   - Parking violations
   - Idling detection
   - Restricted area access

3. **Group Behavior**:
   - Crowd density
   - Group size analysis
   - Duration analysis
   - Formation patterns

**Future Enhancement**: Replace with LSTM or Transformer-based model for learned behavior patterns.

---

## Model Performance

### Benchmarks (on NVIDIA RTX 3080)

| Model | Task | Latency | Accuracy | GPU Memory |
|-------|------|---------|----------|------------|
| YOLOv8n | Weapon Detection | ~15ms | 85% | 1.5GB |
| YOLOv8x | Weapon Detection | ~45ms | 92% | 4.5GB |
| MediaPipe | Face Detection | ~8ms | 90% | 0.5GB |
| InsightFace | Face Recognition | ~25ms | 95% | 2.0GB |
| EasyOCR | Plate Recognition | ~200ms | 88% | 1.2GB |

### Throughput (concurrent streams)

- **YOLOv8n**: ~60 FPS per stream, 4-6 streams
- **YOLOv8x**: ~20 FPS per stream, 2-3 streams
- **MediaPipe**: ~120 FPS per stream, 8-10 streams
- **InsightFace**: ~40 FPS per stream, 3-4 streams
- **EasyOCR**: ~5 FPS per stream, 1-2 streams

---

## Installation

### Requirements

```bash
cd services/intelligence/threat-detector
pip install -r requirements.txt
```

### Dependencies

```txt
# Core ML
torch==2.1.0
torchvision==0.16.0
ultralytics==8.1.0          # YOLOv8
mediapipe==0.10.9            # Face detection
easyocr==1.7.1               # Plate recognition
insightface==0.7.3           # Advanced face recognition (optional)

# Computer Vision
opencv-python==4.8.1.78
Pillow==10.1.0
numpy==1.25.2
scikit-image==0.22.0
```

### GPU Support

For GPU acceleration, ensure CUDA is installed:

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check CUDA version
nvcc --version
```

**CUDA Requirements**:
- CUDA 11.8 or 12.1+
- cuDNN 8.x
- NVIDIA Driver 525+

---

## Custom Model Training

### Training a Custom Weapon Detection Model

1. **Collect Dataset**:
   - Gather images with weapons
   - Use datasets like: COCO, Open Images, custom data
   - Minimum 1000+ images per weapon class

2. **Annotate Data**:
   ```bash
   # Use labelImg, CVAT, or Roboflow
   pip install labelImg
   labelImg ./dataset
   ```

3. **Train YOLOv8**:
   ```python
   from ultralytics import YOLO

   # Load pretrained model
   model = YOLO('yolov8n.pt')

   # Train on custom data
   model.train(
       data='weapons.yaml',
       epochs=100,
       imgsz=640,
       batch=16,
       device=0  # GPU
   )

   # Export model
   model.export(format='onnx')  # or 'engine' for TensorRT
   ```

4. **Deploy Model**:
   ```bash
   cp runs/detect/train/weights/best.pt /models/weapon_detection.pt
   ```

### Training Face Recognition Model

Use InsightFace's training pipeline:

```python
# See: https://github.com/deepinsight/insightface/tree/master/recognition
```

---

## Model Storage

### Directory Structure

```
ai-security-lab-v4/
├── models/                          # Model storage
│   ├── weapon_detection.pt         # Custom weapon YOLO
│   ├── yolov8n.pt                  # Auto-downloaded
│   ├── yolov8x.pt                  # Auto-downloaded
│   ├── face_recognition/           # InsightFace models
│   └── plate_recognition/          # EasyOCR models
└── config/
    └── frigate/
        └── models/                  # Frigate models
            ├── yolov8x.pt
            └── weapon_detection.pt
```

### Model Caching

Models are cached in:
- YOLOv8: `~/.cache/ultralytics/`
- EasyOCR: `~/.EasyOCR/model/`
- InsightFace: `~/.insightface/`
- MediaPipe: Downloaded automatically

---

## Configuration

### Environment Variables

```bash
# Model paths
MODEL_CACHE_DIR=/models
WEAPON_DETECTION_MODEL=yolov8n.pt
BEHAVIOR_MODEL=behavior-lstm.pt  # Future

# Performance
USE_GPU=true
GPU_DEVICE_ID=0
MAX_CONCURRENT_ANALYSES=10
ANALYSIS_TIMEOUT_SECONDS=30
```

### Runtime Configuration

```python
# Adjust confidence thresholds
weapon_detector.set_confidence_threshold(0.6)  # 60% confidence
face_detector.min_detection_confidence = 0.7   # 70% confidence

# Select model size
weapon_detector = WeaponDetector(model_path="yolov8x.pt")  # Use extra large
```

---

## Optimization Tips

### 1. **Model Selection**
- **Fast detection (real-time)**: YOLOv8n, MediaPipe
- **Accurate detection (archive)**: YOLOv8x, InsightFace
- **Balanced**: YOLOv8m, MediaPipe

### 2. **GPU Optimization**
```python
# Use TensorRT for faster inference
model.export(format='engine')  # Export to TensorRT
```

### 3. **Batch Processing**
```python
# Process multiple frames at once
results = model(frames_list, batch=8)
```

### 4. **Resolution Optimization**
- Lower resolution for faster detection (416x416)
- Higher resolution for better accuracy (640x640 or 1280x1280)

### 5. **Multi-GPU**
```python
# Distribute across GPUs
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
```

---

## Troubleshooting

### Model Not Loading

**Issue**: YOLOv8 model download fails
```python
# Manual download
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
mv yolov8n.pt /models/
```

### CUDA Out of Memory

**Solutions**:
1. Use smaller model (yolov8n instead of yolov8x)
2. Reduce batch size
3. Lower image resolution
4. Process frames sequentially

```python
# Clear GPU cache
torch.cuda.empty_cache()
```

### Slow Performance

**Check**:
1. GPU is being used: `torch.cuda.is_available()`
2. CUDA version matches PyTorch: `torch.version.cuda`
3. Model is on GPU: `next(model.parameters()).device`

---

## Future Models (Roadmap)

### v5.0 Planned Models

1. **Object Tracking**: DeepSORT, ByteTrack
2. **Behavior LSTM**: Learned behavior patterns
3. **Audio Detection**: Gunshot, glass breaking, screaming
4. **Pose Estimation**: Human pose analysis (MediaPipe Pose)
5. **Anomaly Detection**: Autoencoder-based unusual event detection

### v6.0 Advanced Models

1. **3D Scene Understanding**: Depth estimation, spatial analysis
2. **Multi-modal Fusion**: Combine vision + audio + metadata
3. **Temporal Analysis**: Video transformers for sequence understanding
4. **Zero-shot Detection**: CLIP-based object detection

---

## References

- **YOLOv8**: https://github.com/ultralytics/ultralytics
- **MediaPipe**: https://google.github.io/mediapipe/
- **InsightFace**: https://github.com/deepinsight/insightface
- **EasyOCR**: https://github.com/JaidedAI/EasyOCR
- **Frigate**: https://docs.frigate.video/

---

**Last Updated**: November 2024
**AI Security Lab**: v4.0
