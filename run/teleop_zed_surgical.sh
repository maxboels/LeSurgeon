#!/bin/bash
# ZED Ultra-Short Range Surgical Teleoperation
# ============================================
# Uses your existing ZED virtual cameras with ultra-short range surgical configuration
# directly with LeRobot teleoperation system.

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🔬 ZED Ultra-Short Range Surgical Teleoperation"
echo "==============================================="
echo "📏 Range: 20-100cm (Ultra-short surgical precision)"
echo "🧠 ZED SDK: NEURAL_PLUS mode with 50% confidence"
echo "🎯 Modalities: Left RGB, Right RGB, Depth, Confidence"
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

echo "🚀 Starting Advanced ZED Pipeline System..."
echo "🎥 Creating virtual video devices: /dev/video10, /dev/video11, /dev/video12"
python src/cameras/advanced_zed_pipeline.py &
PIPELINE_PID=$!

# Wait for pipelines to initialize
echo "⏳ Waiting for ZED pipeline to initialize..."
sleep 8

# Verify virtual devices are created
echo "🔍 Verifying virtual devices..."
for device in /dev/video{10,11,12}; do
    if [ -e "$device" ]; then
        echo "✅ $device created"
    else
        echo "❌ $device not found"
    fi
done
echo ""

echo "🎥 Camera Configuration:"
echo "  - Wrist Camera: /dev/video0 (U20CAM end-effector view)"
echo "  - ZED Left RGB: /dev/video10 (ZED SDK processed left eye)"
echo "  - ZED Right RGB: /dev/video11 (ZED SDK processed right eye)" 
echo "  - ZED Depth: /dev/video12 (ZED SDK neural depth 20-100cm)"
echo ""
echo "🔬 ZED SDK Processing:"
echo "  - Neural depth processing (20-100cm surgical range)"
echo "  - 50% confidence threshold for balanced precision"
echo "  - Real-time left RGB, right RGB, depth, and confidence maps"
echo ""

echo "🚀 Starting ZED Ultra-Short Range Teleoperation..."
echo "📊 Recording interface will show:"
echo "  1. Wrist camera (close-up surgical view)"
echo "  2. ZED Left RGB (left eye processed view)"
echo "  3. ZED Right RGB (right eye processed view)"
echo "  4. ZED Depth (neural depth 20-45cm)"
echo ""
echo "🎮 Controls:"
echo "  - Move leader arm to control follower"
echo "  - All camera streams will be recorded"
echo "  - Press Ctrl+C to stop"
echo ""

# Start teleoperation with wrist + ZED virtual cameras using 20-45cm surgical range
printf "\n\n" | python -m lerobot.teleoperate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id=lesurgeon_follower_arm \
  --robot.cameras="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, zed_left: {type: opencv, index_or_path: /dev/video10, width: 1280, height: 720, fps: 30}, zed_right: {type: opencv, index_or_path: /dev/video11, width: 1280, height: 720, fps: 30}, zed_depth: {type: opencv, index_or_path: /dev/video12, width: 1280, height: 720, fps: 30}}" \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id=lesurgeon_leader_arm \
  --display_data=true

echo ""
echo "✅ ZED Ultra-Short Range Surgical Teleoperation completed"

# Cleanup ZED pipeline
echo "🧹 Cleaning up ZED pipeline..."
if [ ! -z "$PIPELINE_PID" ]; then
    kill $PIPELINE_PID 2>/dev/null || true
    echo "✅ ZED pipeline stopped"
fi

echo "📁 Recorded data includes:"
echo "  - Wrist camera frames (surgical close-up)"
echo "  - ZED Left RGB (processed left eye view)"
echo "  - ZED Right RGB (processed right eye view)"
echo "  - ZED Depth (neural depth 20-100cm surgical range)"
echo "  - Robot joint positions and actions"
echo "  - Timestamps synchronized across all modalities"