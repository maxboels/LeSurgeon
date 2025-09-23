#!/bin/bash
# 5-Modality Surgical Teleoperation
# =================================
# Custom teleoperation with ZED SDK + wrist cameras
# Provides all 5 modalities for surgical robotics

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎥 Starting 5-Modality Surgical Teleoperation..."
echo "================================================"
echo ""
echo "📊 Camera Modalities:"
echo "  🔬 ZED Laparoscope:"
echo "    - Left RGB (stereo left eye)"
echo "    - Right RGB (stereo right eye)" 
echo "    - Depth Map (surgical range 20-100cm)"
echo "  🦾 Wrist Cameras:"
echo "    - Left Arm Wrist"
echo "    - Right Arm Wrist (if connected)"
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

# Check ZED camera availability
echo "🔍 Checking ZED camera..."
if lsusb | grep -q "ZED"; then
    echo "✅ ZED camera detected"
else
    echo "⚠️  ZED camera not detected via USB"
fi

# Check wrist cameras
echo "🔍 Checking wrist cameras..."
if [ -e "/dev/video0" ]; then
    echo "✅ Left wrist camera: /dev/video0"
else
    echo "❌ Left wrist camera not found: /dev/video0"
fi

if [ -e "/dev/video2" ]; then
    echo "✅ Right wrist camera: /dev/video2"
else
    echo "⚠️  Right wrist camera not found: /dev/video2 (unplugged as expected)"
fi

echo ""
echo "🎮 Teleoperation Controls:"
echo "  - Move LEADER arm to control FOLLOWER"
echo "  - Camera feeds will display in separate windows"
echo "  - Press 'q' in any camera window to quit"
echo "  - Press Ctrl+C to stop teleoperation"
echo ""

# Activate environment
source .lerobot/bin/activate

# Export detected ports
export LEADER_PORT="$LEADER_PORT"
export FOLLOWER_PORT="$FOLLOWER_PORT"

# Run 5-modality teleoperation
echo "🚀 Starting teleoperation..."
echo ""
python src/five_modality_teleop.py