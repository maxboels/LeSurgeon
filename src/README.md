# LeSurgeon Source Code

This directory contains the core production code for the LeSurgeon surgical robotics system with ZED SDK integration.

## Directory Structure

```
src/
├── __init__.py                    # Main package initialization
├── cameras/                       # Camera system modules (ZED SDK production)
│   ├── __init__.py               # Camera package exports
│   ├── zed_sdk_camera.py         # ZED SDK camera wrapper (production)
│   ├── zed_multimodal_camera.py  # ZED 2 stereo camera with depth & 3D
│   ├── lerobot_zed_integration.py # LeRobot-compatible ZED interface
│   └── multimodal_collector.py   # Multi-modal data collection
├── zed_tests/                     # ZED camera testing scripts
│   ├── test_zed_sdk_installation.py      # Verify ZED SDK functionality
│   ├── test_zed_multimodal_display.py    # Multi-modal display testing
│   ├── test_zed_multimodal_setup.py      # Setup verification
│   ├── test_zed_stereo_teleop.py         # Stereo teleoperation testing
│   ├── test_zed_cameras_no_display.py    # Headless camera testing
│   └── test_zed_wrapper_quick.py         # Quick ZED wrapper testing
└── utils/                         # Utility modules
    ├── __init__.py               # Utils package exports
    └── detect_cameras.sh         # Smart camera detection script
```

## ZED Camera System

The camera system provides multi-modal surgical robotics data capture using the official ZED SDK:

### ZED 2 Ultra-Short Range Surgical Configuration
- **Optimized Range**: 20-45cm (surgical workspace optimized)
- **Precision**: ±44mm surgical-grade depth accuracy  
- **Depth Mode**: NEURAL_PLUS with 90% confidence threshold
- **Frame Rate**: 10.3 FPS real-time multi-modal processing
- **Resolution**: 1280×720 per eye stereo capture

### ZED SDK Features for Surgical Robotics
- **6 Modalities**: Wrist cam + ZED left/right RGB + depth + confidence + point cloud
- **Real-time Processing**: Hardware-accelerated CUDA depth computation
- **Surgical Precision**: Ultra-short range optimization for surgical tasks
- **LeRobot Integration**: Ready for teleoperation and policy training

### Usage Examples

```python
# Production ZED SDK camera
from src.cameras import ZEDSDKCamera

camera = ZEDSDKCamera(
    resolution='HD720',
    depth_mode='NEURAL_PLUS',  # Ultra-high precision for surgery
    sensing_mode='STANDARD',   # Real-time performance
    depth_minimum_distance=200, # 20cm surgical range
    depth_maximum_distance=450  # 45cm surgical range
)

# Get all surgical modalities
left_rgb, right_rgb, depth, confidence = camera.capture_multimodal()

# LeRobot-compatible interface
from src.cameras import LeRobotZEDCamera

lerobot_camera = LeRobotZEDCamera(
    resolution='hd',
    surgical_range=True,        # Enable 20-45cm optimization
    include_depth=True,
    include_confidence=True
)
```

## Live Multi-Modal Display

Test the complete surgical vision system:

```bash
# Real-time 4-view surgical display
python debug/zed_experiments/live_surgical_multimodal.py

# Ultra-short range configuration
python debug/zed_experiments/zed_ultra_short_range.py

# Test ZED SDK integration
python src/zed_tests/test_zed_sdk_installation.py
```
## Integration with LeRobot

The enhanced camera system integrates with LeRobot teleoperation:

```bash
# ZED multi-modal teleoperation (6 modalities)
bash run/teleoperate_zed_multimodal.sh

# Record training data with ZED surgical vision
./lesurgeon.sh record --zed-multimodal --surgical-range

# Train policies with spatial depth understanding
./lesurgeon.sh train --zed-enhanced --depth-modality
```

## Testing and Verification

Comprehensive testing suite for ZED integration:

```bash
# Test ZED SDK installation and functionality
python src/zed_tests/test_zed_sdk_installation.py

# Test multi-modal capture and display
python src/zed_tests/test_zed_multimodal_display.py

# Verify surgical range optimization
python src/zed_tests/test_zed_stereo_teleop.py

# Quick functionality check
python src/zed_tests/test_zed_wrapper_quick.py
```

## Architecture: Development vs Production

- **`src/cameras/`** - Production-ready ZED SDK integration
- **`src/zed_tests/`** - ZED functionality testing and verification  
- **`debug/zed_experiments/`** - ZED research and experimental development
- **`setup/install_zed_sdk.sh`** - ZED SDK 5.0.6 installation script

This organization ensures clean separation between production robotics code, testing infrastructure, and experimental development for the LeSurgeon surgical robotics platform.