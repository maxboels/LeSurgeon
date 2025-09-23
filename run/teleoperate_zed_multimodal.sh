#!/bin/bash
# Dynamic ARM Teleoperation with Multi-Modal Camera Support
# Automatically detects the correct ports and configures cameras (ZED 2 + U20CAM)

# Source the port detection and camera detection utilities
source "$(dirname "$0")/../debug/detect_arm_ports.sh"
source "$(dirname "$0")/../src/utils/detect_cameras.sh"

echo "🎮 Starting teleoperation with multi-modal camera support..."
echo ""

# Detect arm ports
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

# Detect cameras and get configuration
echo "🔍 Detecting available cameras..."
eval $(get_camera_config)

echo "📷 Camera Configuration Detected:"
echo "  Mode: $CAMERA_MODE" 
echo "  Description: $CAMERA_DESCRIPTION"
echo "  Configuration: $CAMERA_CONFIG"
echo ""
echo "🤖 Robot Configuration:"
echo "  - Follower: $FOLLOWER_PORT"
echo "  - Leader:   $LEADER_PORT"
echo ""

# Show what the user will see
case "$CAMERA_MODE" in
    "zed_only_multimodal"|"zed_multimodal")
        echo "🎥 You will see in the recorder interface:"
        echo "  - ZED Left: Left eye RGB view (1280x720)" 
        echo "  - ZED Right: Right eye RGB view (1280x720)"
        echo "  - ZED Depth: Real-time depth map from stereo matching"
        echo "  - ZED PointCloud: 3D point cloud visualization"
        echo "  💡 Full multi-modal ZED 2 data for advanced spatial training!"
        ;;
    "hybrid_multimodal"|"hybrid")
        echo "🎥 You will see in the recorder interface:"
        echo "  - Wrist: U20CAM close-up view (1280x720)"
        echo "  - ZED Left: Left eye RGB view (1280x720)"
        echo "  - ZED Right: Right eye RGB view (1280x720)" 
        echo "  - ZED Depth: Real-time depth map"
        echo "  - ZED PointCloud: 3D spatial data"
        echo "  💡 Best setup: detailed wrist view + rich ZED spatial data!"
        ;;
    "standard"|"u20cam_only")
        echo "🎥 You will see in the recorder interface:"
        echo "  - Wrist: U20CAM wrist view (1280x720)"
        echo "  - External: U20CAM external view (2560x720)"
        echo "  💡 Standard dual-camera setup"
        ;;
esac

echo ""
echo "🔧 To stop teleoperation: Press Ctrl+C in this terminal"
echo ""

source .lerobot/bin/activate

# Use the detected camera configuration
printf "\n\n" | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="$CAMERA_CONFIG" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true