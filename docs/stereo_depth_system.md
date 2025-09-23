# Stereo-Depth ZED Pipeline System 🎭

## Overview

This is a **professional-grade video streaming system** that creates stereo-depth camera streams for LeRobot teleoperation:

1. **ZED Left RGB** → `/dev/video10`
2. **ZED Right RGB** → `/dev/video11` 
3. **ZED Depth** → `/dev/video12`
4. **Left Wrist Camera** → `/dev/video0` (if available)
5. **Right Wrist Camera** → `/dev/video1` (if available)

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐
│   ZED SDK       │    │  Python      │    │  FFmpeg       │    │ LeRobot     │
│   (Hardware)    │───▶│  Virtual     │───▶│  Pipeline     │───▶│ OpenCV      │
│                 │    │  Cameras     │    │               │    │ Reader      │
└─────────────────┘    └──────────────┘    └───────────────┘    └─────────────┘

ZED Left  ───┐
ZED Right ───┼──▶ Named Pipes ──▶ FFmpeg ──▶ v4l2sink ──▶ /dev/videoX ──▶ LeRobot
ZED Depth ───┘
```

## Key Components

### 1. ZED Virtual Cameras (`src/cameras/zed_virtual_cameras.py`)
- **ZEDLeftCamera**: Left RGB stream from ZED SDK
- **ZEDRightCamera**: Right RGB stream from ZED SDK  
- **ZEDDepthCamera**: Depth map with surgical-optimized processing

### 2. Advanced Pipeline (`src/cameras/advanced_zed_pipeline.py`)
- **FFmpegZEDPipeline**: Individual FFmpeg pipeline per camera
- **AdvancedZEDCameraSystem**: Complete system manager
- Uses **Named Pipes** + **FFmpeg** + **v4l2loopback** for professional video streaming

### 3. Teleoperation Script (`run/advanced_5_modality_teleop.sh`)
- **LeRobot-native** integration
- Automatic device detection and configuration
- Proper cleanup and error handling

## Usage

### Quick Start
```bash
# 1. Verify system is ready
python debug/verify_advanced_pipeline.py

# 2. Run 5-modality teleoperation
./run/advanced_5_modality_teleop.sh
```

### Manual Testing
```bash
# Test just the pipeline
python src/cameras/advanced_zed_pipeline.py

# Check created devices
ls -la /dev/video{10,11,12}

# Test with OpenCV
python -c "import cv2; cap = cv2.VideoCapture(10); print(cap.read()[0])"
```

## Technical Details

### Video Specifications
- **Resolution**: 1280×720 @ 30 FPS
- **Format**: BGR24 → YUYV422 (FFmpeg conversion)
- **Surgical Range**: 20-100cm depth optimization
- **Depth Mode**: NEURAL_PLUS for highest quality

### Device Mapping
```
/dev/video10 → ZED Left RGB
/dev/video11 → ZED Right RGB  
/dev/video12 → ZED Depth (colorized)
/dev/video0  → Left Wrist Camera
/dev/video1  → Right Wrist Camera
```

### LeRobot Configuration
```yaml
cameras:
  zed_left: {type: opencv, index_or_path: /dev/video10}
  zed_right: {type: opencv, index_or_path: /dev/video11}
  zed_depth: {type: opencv, index_or_path: /dev/video12}
  left_wrist: {type: opencv, index_or_path: /dev/video0}
  right_wrist: {type: opencv, index_or_path: /dev/video1}
```

## Advanced Features

### Professional Video Streaming
- **Named Pipes**: High-performance inter-process communication
- **FFmpeg Processing**: Industry-standard video pipeline
- **v4l2loopback**: Linux virtual video device creation
- **Thread-Safe**: Concurrent multi-camera processing

### Surgical Optimization
- **Depth Range**: 20cm-100cm surgical workspace
- **Neural Depth**: AI-enhanced depth estimation
- **Color-coded Depth**: Intuitive depth visualization
- **Real-time Processing**: 30 FPS with minimal latency

### Error Handling
- **Graceful Degradation**: System continues with available cameras
- **Automatic Cleanup**: Proper resource management on exit
- **Comprehensive Logging**: Detailed status and performance metrics

## Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   ```bash
   source setup/activate_lerobot.sh
   ```

2. **"Permission denied" for /dev/videoX**:
   ```bash
   sudo usermod -a -G video $USER
   # Then logout/login
   ```

3. **v4l2loopback not working**:
   ```bash
   sudo modprobe -r v4l2loopback
   sudo modprobe v4l2loopback devices=3 video_nr=10,11,12
   ```

### Performance Optimization

1. **CPU Usage**: Each pipeline uses ~5-10% CPU
2. **Memory**: ~100MB per active camera
3. **Latency**: <50ms end-to-end
4. **Bandwidth**: ~30MB/s per 720p stream

## Verification

The system includes comprehensive testing:

```bash
python debug/verify_advanced_pipeline.py
```

Tests verify:
- ✅ ZED SDK virtual cameras
- ✅ v4l2loopback module  
- ✅ FFmpeg with v4l2 support
- ✅ Virtual device creation
- ✅ Named pipe functionality

## Next Steps

1. **Data Collection**: Use with `lerobot.record` for dataset creation
2. **Training**: Feed into ACT or other imitation learning algorithms  
3. **Real-time Inference**: Deploy trained models with this camera setup
4. **Performance Tuning**: Optimize for your specific hardware setup

## Why This Approach?

- **Professional Grade**: Uses industry-standard video streaming tools
- **LeRobot Native**: Full compatibility with LeRobot ecosystem
- **Scalable**: Easy to add more cameras or modalities
- **Maintainable**: Clean architecture with proper separation of concerns
- **Educational**: Learn advanced video pipeline concepts

This system represents a **sophisticated integration** of computer vision, robotics, and video streaming technologies specifically designed for surgical robotics teleoperation! 🔬🤖