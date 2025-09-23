#!/bin/bash
# Dynamic Stereo and Wrist Camera Teleoperation 
# =============================================
# Base: wrist camera + stereo camera raw feed
# Optional: --depth (stereo depth), --wrist-right (right wrist camera)

# Parse arguments
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
            echo "Dynamic teleoperation with configurable cameras"
            echo ""
            echo "Base cameras (always included):"
            echo "  - Wrist Left: /dev/video0 (640x480)"
            echo "  - Stereo Feed: /dev/video2 (1344x376 concatenated)"
            echo ""
            echo "Optional cameras:"
            echo "  --depth        Add stereo depth camera (requires virtual bridge)"
            echo "  --wrist-right  Add right wrist camera (/dev/video1)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Basic 2-camera setup"
            echo "  $0 --depth           # 3-camera with stereo depth"
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

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🔬 Dynamic Stereo and Wrist Camera Teleoperation"
echo "==============================================="
echo "�� Base: Wrist + Stereo Feed (always enabled)"
if [ "$USE_DEPTH" = true ]; then
    echo "📷 Optional: Stereo Depth (--depth enabled)"
fi
if [ "$USE_WRIST_RIGHT" = true ]; then
    echo "📷 Optional: Right Wrist (--wrist-right enabled)"
fi
echo ""

# Detect arm ports
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

# Start stereo bridge if depth is needed
if [ "$USE_DEPTH" = true ]; then
    echo "🚀 Starting Stereo Virtual Bridge (depth camera needed)..."
    python test_zed_virtual_bridge.py &
    BRIDGE_PID=$!
    echo "⏳ Waiting for stereo bridge to initialize..."
    sleep 8
fi

# Build camera configuration
CAMERA_COUNT=2
CAMERA_CONFIG="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, stereo: {type: opencv, index_or_path: /dev/video2, width: 1344, height: 376, fps: 30}"

if [ "$USE_WRIST_RIGHT" = true ]; then
    CAMERA_CONFIG="${CAMERA_CONFIG}, wrist_right: {type: opencv, index_or_path: /dev/video1, width: 640, height: 480, fps: 30}"
    CAMERA_COUNT=$((CAMERA_COUNT + 1))
fi

if [ "$USE_DEPTH" = true ]; then
    CAMERA_CONFIG="${CAMERA_CONFIG}, stereo_depth: {type: opencv, index_or_path: /dev/video11, width: 1280, height: 720, fps: 30}"
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
    echo "  - Stereo Depth: /dev/video11 (Processed depth 20-50cm)"
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
        echo "  4. Stereo depth (processed depth 20-50cm)"
    else
        echo "  3. Stereo depth (processed depth 20-50cm)"
    fi
fi
echo ""
echo "🎮 Controls:"
echo "  - Move leader arm to control follower"
echo "  - All camera streams will be recorded"
echo "  - Press Ctrl+C to stop"
echo ""

# Start teleoperation with dynamic camera configuration
printf "\n\n" | python -m lerobot.teleoperate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id=lesurgeon_follower_arm \
  --robot.cameras="$CAMERA_CONFIG" \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id=lesurgeon_leader_arm \
  --display_data=true

echo ""
echo "✅ ${CAMERA_COUNT}-Camera Teleoperation completed"

# Cleanup stereo bridge if it was started
if [ "$USE_DEPTH" = true ] && [ ! -z "$BRIDGE_PID" ]; then
    echo "🧹 Cleaning up stereo bridge..."
    kill $BRIDGE_PID 2>/dev/null || true
    echo "✅ Stereo bridge stopped"
fi

echo "📁 Recorded data includes:"
echo "  - Wrist camera frames (close-up view)"
echo "  - Stereo feed frames (concatenated left+right views)"
if [ "$USE_WRIST_RIGHT" = true ]; then
    echo "  - Right wrist camera frames (close-up view)"
fi
if [ "$USE_DEPTH" = true ]; then
    echo "  - Stereo depth frames (processed depth 20-50cm)"
fi
echo "  - Robot joint positions and actions"
echo "  - Timestamps synchronized across modalities"
