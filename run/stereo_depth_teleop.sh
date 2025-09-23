#!/bin/bash
# Stereo-Depth Surgical Teleoperation with LeRobot
# ===============================================
# Uses advanced FFmpeg pipeline to create stereo-depth camera streams:
# - ZED Left RGB, ZED Right RGB, ZED Depth, Left Wrist, Right Wrist

set -e

echo "🎭 Stereo-Depth Surgical Teleoperation Setup"
echo "============================================"

# Configuration
BASE_DIR="$HOME/projects/LeSurgeon"
cd "$BASE_DIR"

# Activate LeRobot environment
echo "🔌 Activating LeRobot environment..."
source setup/activate_lerobot.sh

# Verify arms are connected
echo "🦾 Verifying robotic arms..."
if ! python -c "from lerobot.robots.so101_follower import SO101Follower; from lerobot.teleoperators.so101_leader import SO101Leader; print('SO101 classes imported successfully')" 2>/dev/null; then
    echo "❌ Failed to import SO101 classes. Please check arm connections."
    echo "Run: python debug/diagnose_motors.py"
    exit 1
fi

# Get arm mappings
source setup/arm_mapping.conf
echo "📍 Leader arm: $LEADER_ARM_PORT"
echo "📍 Follower arm: $FOLLOWER_ARM_PORT"

echo ""
echo "🚀 Starting Advanced ZED Pipeline System..."
echo "=========================================="

# Start the advanced pipeline in background
echo "📡 Launching FFmpeg ZED pipelines..."
python src/cameras/advanced_zed_pipeline.py &
PIPELINE_PID=$!

# Wait for pipelines to start
echo "⏳ Waiting for pipelines to initialize..."
sleep 10

# Verify virtual devices are created
echo "🔍 Verifying virtual devices..."
for device in /dev/video{10,11,12}; do
    if [[ -e "$device" ]]; then
        echo "✅ Found: $device"
    else
        echo "❌ Missing: $device"
        kill $PIPELINE_PID 2>/dev/null || true
        exit 1
    fi
done

# Check for wrist cameras
echo "🔍 Checking for wrist cameras..."
WRIST_CAMERAS=""
if [[ -e "/dev/video0" ]]; then
    echo "✅ Found left wrist camera: /dev/video0"
    WRIST_CAMERAS="$WRIST_CAMERAS left_wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30},"
fi
if [[ -e "/dev/video1" ]]; then
    echo "✅ Found right wrist camera: /dev/video1"
    WRIST_CAMERAS="$WRIST_CAMERAS right_wrist: {type: opencv, index_or_path: /dev/video1, width: 1280, height: 720, fps: 30},"
fi

# Build complete camera configuration
CAMERA_CONFIG="{
    zed_left: {type: opencv, index_or_path: /dev/video10, width: 1280, height: 720, fps: 30},
    zed_right: {type: opencv, index_or_path: /dev/video11, width: 1280, height: 720, fps: 30},
    zed_depth: {type: opencv, index_or_path: /dev/video12, width: 1280, height: 720, fps: 30},$WRIST_CAMERAS
}"

# Remove trailing comma
CAMERA_CONFIG=$(echo "$CAMERA_CONFIG" | sed 's/,$WRIST_CAMERAS//')

echo ""
echo "🎯 Stereo-Depth Camera Configuration:"
echo "===================================="
echo "$CAMERA_CONFIG"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    if [[ -n "$PIPELINE_PID" ]]; then
        kill $PIPELINE_PID 2>/dev/null || true
    fi
    # Remove virtual devices
    sudo modprobe -r v4l2loopback 2>/dev/null || true
    echo "✅ Cleanup complete"
}
trap cleanup EXIT

echo "🎮 Starting LeRobot Teleoperation..."
echo "===================================="

# LeRobot teleoperation command
python -m lerobot.scripts.control_robot teleoperate \
    --robot-path lerobot.common.robot_devices.robots.so101 \
    --robot-overrides '{
        leader_arms: [{
            _target_: lerobot.common.robot_devices.robots.so101.SO101Robot,
            port: "'$LEADER_ARM_PORT'",
            start_arm: true,
            mock: false
        }],
        follower_arms: [{
            _target_: lerobot.common.robot_devices.robots.so101.SO101Robot,
            port: "'$FOLLOWER_ARM_PORT'",
            start_arm: true,
            mock: false
        }]
    }' \
    --fps 30 \
    --robot.cameras="$CAMERA_CONFIG" \
    --display-cameras

echo ""
echo "🏁 Stereo-depth teleoperation session ended."