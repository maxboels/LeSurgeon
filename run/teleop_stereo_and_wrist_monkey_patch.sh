#!/bin/bash
# ZED Monkey Patch Stereo and Wrist Camera Teleoperation 
# =======================================================
# Uses OpenCV monkey patch to integrate ZED SDK depth instead of broken virtual bridge

# Parse arguments (same as before)
USE_DEPTH=false
USE_WRIST_RIGHT=false

for arg in "$@"; do
    case $arg in
        --depth)
            USE_DEPTH=true
            shift
            ;;
        --wrist-right)
            USE_WRIST_RIGHT=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "ZED-Enhanced teleoperation with ZED SDK depth"
            echo ""
            echo "Base cameras (always included):"
            echo "  - Wrist Left: /dev/video0 (640x480)"
            echo "  - Stereo Feed: /dev/video2 (1344x376 concatenated)"
            echo ""
            echo "Optional cameras:"
            echo "  --depth        Add ZED SDK depth camera (NEURAL_PLUS mode)"
            echo "  --wrist-right  Add right wrist camera (/dev/video1)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Basic 2-camera setup"
            echo "  $0 --depth           # 3-camera with ZED SDK depth"
            echo "  $0 --wrist-right     # 3-camera with right wrist"
            echo "  $0 --depth --wrist-right  # Full 4-camera setup"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Source the port detection utility (same as before)
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🐒 ZED Monkey Patch Stereo and Wrist Camera Teleoperation"
echo "=========================================================="
echo "🔬 Base: Wrist + Stereo Feed (always enabled)"
if [ "$USE_DEPTH" = true ]; then
    echo "🧠 Optional: ZED SDK Depth (NEURAL_PLUS monkey patch)"
fi
if [ "$USE_WRIST_RIGHT" = true ]; then
    echo "📷 Optional: Right Wrist (--wrist-right enabled)"
fi
echo ""

# Detect arm ports (same as before)
echo "🔍 Detecting ARM ports..."
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "✅ Robot Configuration:"
echo "  - Leader:   $LEADER_PORT"
echo "  - Follower: $FOLLOWER_PORT"
echo ""

# Activate LeRobot environment
source .lerobot/bin/activate

# Enable ZED OpenCV patch if depth is needed
if [ "$USE_DEPTH" = true ]; then
    echo "🔧 Enabling ZED SDK integration..."
    # Create Python script to enable patch and run teleoperation
    cat > /tmp/zed_patched_teleop.py << EOF
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path("$PWD")
sys.path.insert(0, str(project_root))

# Enable ZED patch BEFORE importing lerobot
from zed_opencv_patch import enable_zed_opencv_patch, disable_zed_opencv_patch

print("🔧 Enabling ZED OpenCV patch...")
enable_zed_opencv_patch()

# Now run lerobot teleoperation
import subprocess
import signal

def signal_handler(signum, frame):
    print("🔧 Disabling ZED OpenCV patch...")
    disable_zed_opencv_patch()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    # Run the teleoperation command
    cmd = sys.argv[1:]  # Get command from arguments
    result = subprocess.run(cmd, check=False)
    sys.exit(result.returncode)
finally:
    print("🔧 Disabling ZED OpenCV patch...")
    disable_zed_opencv_patch()
EOF
    
    PYTHON_WRAPPER="python /tmp/zed_patched_teleop.py"
else
    PYTHON_WRAPPER=""
fi

# Build camera configuration (same as before)
CAMERA_COUNT=2
CAMERA_CONFIG="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, stereo: {type: opencv, index_or_path: /dev/video2, width: 640, height: 376, fps: 30}"

if [ "$USE_WRIST_RIGHT" = true ]; then
    CAMERA_CONFIG="${CAMERA_CONFIG}, wrist_right: {type: opencv, index_or_path: /dev/video1, width: 640, height: 480, fps: 30}"
    CAMERA_COUNT=$((CAMERA_COUNT + 1))
fi

if [ "$USE_DEPTH" = true ]; then
    # Use /dev/video11 which will be intercepted by our patch
    CAMERA_CONFIG="${CAMERA_CONFIG}, zed_depth: {type: opencv, index_or_path: /dev/video11, width: 1280, height: 720, fps: 30}"
    CAMERA_COUNT=$((CAMERA_COUNT + 1))
fi

CAMERA_CONFIG="${CAMERA_CONFIG}}"

echo "🎥 Camera Configuration ($CAMERA_COUNT cameras):"
echo "  - Wrist Left: /dev/video0 (USB camera - close-up view)"
echo "  - Stereo Feed: /dev/video2 (Raw concatenated left+right views)"
if [ "$USE_WRIST_RIGHT" = true ]; then
    echo "  - Wrist Right: /dev/video1 (USB camera - close-up view)"
fi
if [ "$USE_DEPTH" = true ]; then
    echo "  - ZED Depth: /dev/video11 (ZED SDK NEURAL_PLUS depth 20-50cm)"
fi
echo ""

echo "🚀 Starting ${CAMERA_COUNT}-Camera Teleoperation..."
echo "📊 Recording interface will show:"
echo "  1. Wrist camera (close-up view)"
echo "  2. Stereo feed (concatenated left+right views)"
if [ "$USE_WRIST_RIGHT" = true ]; then
    echo "  3. Right wrist camera (close-up view)"
fi
if [ "$USE_DEPTH" = true ]; then
    if [ "$USE_WRIST_RIGHT" = true ]; then
        echo "  4. ZED depth (ZED SDK processed depth 20-50cm)"
    else
        echo "  3. ZED depth (ZED SDK processed depth 20-50cm)"
    fi
fi
echo ""
echo "🎮 Controls:"
echo "  - Move leader arm to control follower"
echo "  - All camera streams will be recorded"
echo "  - Press Ctrl+C to stop"
echo ""

# Start teleoperation
if [ "$USE_DEPTH" = true ]; then
    # Use Python wrapper to enable ZED patch
    printf "\n\n" | $PYTHON_WRAPPER python -m lerobot.teleoperate \
      --robot.type=so101_follower \
      --robot.port="$FOLLOWER_PORT" \
      --robot.id=lesurgeon_follower_arm \
      --robot.cameras="$CAMERA_CONFIG" \
      --teleop.type=so101_leader \
      --teleop.port="$LEADER_PORT" \
      --teleop.id=lesurgeon_leader_arm \
      --display_data=true
else
    # Run normally without ZED patch
    printf "\n\n" | python -m lerobot.teleoperate \
      --robot.type=so101_follower \
      --robot.port="$FOLLOWER_PORT" \
      --robot.id=lesurgeon_follower_arm \
      --robot.cameras="$CAMERA_CONFIG" \
      --teleop.type=so101_leader \
      --teleop.port="$LEADER_PORT" \
      --teleop.id=lesurgeon_leader_arm \
      --display_data=true
fi

echo ""
echo "✅ ${CAMERA_COUNT}-Camera Teleoperation completed"

# Cleanup
if [ "$USE_DEPTH" = true ]; then
    rm -f /tmp/zed_patched_teleop.py
fi

echo "📁 Recorded data includes:"
echo "  - Wrist camera frames (close-up view)"
echo "  - Stereo feed frames (concatenated left+right views)"
if [ "$USE_WRIST_RIGHT" = true ]; then
    echo "  - Right wrist camera frames (close-up view)"
fi
if [ "$USE_DEPTH" = true ]; then
    echo "  - ZED depth frames (ZED SDK processed depth 20-50cm)"
fi
echo "  - Robot joint positions and actions"
echo "  - Timestamps synchronized across modalities"