# LeSurgeon Source Code

This directory contains the core production code for the LeSurgeon surgical robotics system.

## Directory Structure

```
src/
├── __init__.py                    # Main package initialization
├── cameras/                       # Camera system modules
│   ├── __init__.py               # Camera package exports
│   ├── zed_multimodal_camera.py  # ZED 2 stereo camera with depth & 3D
│   ├── lerobot_zed_integration.py # LeRobot-compatible ZED interface
│   └── multimodal_collector.py   # Multi-modal data collection
└── utils/                        # Utility modules
    ├── __init__.py               # Utils package exports
    └── detect_cameras.sh         # Smart camera detection script
```

## Camera System

The camera system provides multi-modal data capture for enhanced surgical robotics:

### ZED 2 Stereo Camera Features
- **Stereo RGB**: 1280×720 per eye at 2560×720 combined resolution
- **Depth Maps**: Real-time stereo matching using SGBM algorithm
- **3D Point Clouds**: Generated from depth + RGB for spatial understanding
- **Multi-Resolution**: Fast (640×360), HD (1280×720), FHD (1920×1080) modes

### Usage Examples

```python
# Basic ZED multi-modal camera
from src.cameras import ZEDMultiModalCamera

camera = ZEDMultiModalCamera(
    width=2560, height=720, fps=30,
    compute_depth=True, compute_pointcloud=True
)

# LeRobot-compatible interface
from src.cameras import LeRobotZEDCamera

lerobot_camera = LeRobotZEDCamera(
    resolution='hd',
    include_depth=True,
    include_pointcloud=True
)

# Multi-modal data collection
from src.cameras import MultiModalCollector

collector = MultiModalCollector(
    output_dir="outputs/multimodal_data",
    zed_resolution="hd",
    save_pointclouds=True,
    save_depth_maps=True
)
```

## Integration with Scripts

The run/ scripts now use the enhanced camera system:

```bash
# Record with ZED 2 multi-modal data
./lesurgeon.sh record --enhanced-zed --zed-resolution hd

# Run inference with enhanced spatial data
./lesurgeon.sh inference --enhanced-zed --zed-resolution fhd
```

## Testing

Test the reorganization with:

```bash
# Test all camera modules
./lesurgeon.sh test-cameras

# Or run directly
python test_camera_reorganization.py
```

## Development vs Production

- `src/` - Production code used in real robotics operations
- `debug/` - Development tools for testing and exploration
- `run/` - Operation scripts that use src/ modules

This separation ensures clean, maintainable code architecture for the LeSurgeon surgical robotics platform.