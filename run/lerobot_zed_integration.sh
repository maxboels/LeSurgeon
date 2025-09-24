#!/bin/bash
# LeRobot ZED Integration Script
# =============================
# Use ZED 2i cameras directly with LeRobot teleoperation system

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎥 LeRobot ZED Integration"
echo "========================="
echo "Direct ZED SDK integration with LeRobot teleoperation"
echo ""

# Detect ARM ports
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
echo "📷 Checking ZED camera..."
if lsusb | grep -q "ZED"; then
    echo "✅ ZED camera detected via USB"
elif python -c "import pyzed.sl as sl; cam = sl.Camera(); print('ZED SDK available')" 2>/dev/null; then
    echo "✅ ZED SDK available"
else
    echo "❌ ZED camera or SDK not detected"
    echo "Please check:"
    echo "  1. ZED camera is connected"
    echo "  2. ZED SDK is installed: ./setup/install_zed_sdk.sh"
    exit 1
fi

# Check if wrist camera is available
if [ -e "/dev/video0" ]; then
    echo "✅ Wrist camera detected: /dev/video0"
    WRIST_CAM_CONFIG='"wrist": {"type": "opencv", "index_or_path": "/dev/video0", "width": 1280, "height": 720, "fps": 30},'
else
    echo "⚠️  No wrist camera found at /dev/video0"
    WRIST_CAM_CONFIG=""
fi

echo ""
echo "🎯 Camera Modalities Available:"
echo "  📷 ZED Left RGB - Spatial context (1280×720)"
echo "  📷 ZED Right RGB - Stereo pair (1280×720)"  
echo "  🔍 ZED Depth - 3D spatial info (20-50cm surgical range)"
echo "  📷 Wrist Camera - Close-up detail (if available)"
echo ""

# Activate LeRobot environment
source .lerobot/bin/activate

# Method 1: Use Python camera factory (Recommended)
echo "🚀 Method 1: Using Python Camera Factory Integration"
echo "===================================================="

# Create the camera configuration string
PYTHON_CAMERA_CONFIG="{
    ${WRIST_CAM_CONFIG}
    \"zed_left\": {
        \"type\": \"python\",
        \"module\": \"src.cameras.zed_lerobot_camera\", 
        \"class\": \"LeRobotZEDCamera\",
        \"config\": {\"modality\": \"rgb_left\", \"surgical_range\": true, \"width\": 1280, \"height\": 720, \"fps\": 30}
    },
    \"zed_depth\": {
        \"type\": \"python\",
        \"module\": \"src.cameras.zed_lerobot_camera\",
        \"class\": \"LeRobotZEDCamera\", 
        \"config\": {\"modality\": \"depth\", \"surgical_range\": true, \"width\": 1280, \"height\": 720, \"fps\": 30}
    }
}"

echo "📝 Camera Configuration:"
echo "$PYTHON_CAMERA_CONFIG"
echo ""

echo "🎮 Starting LeRobot teleoperation with ZED integration..."
echo "🔧 Controls:"
echo "  - Move leader arm to control follower"
echo "  - ZED cameras provide spatial context and depth"
echo "  - All feeds visible in rerun.io visualization"
echo "  - Press Ctrl+C to stop"
echo ""

# Check if LeRobot supports Python cameras (depends on version)
if python -c "from lerobot.cameras.python_camera import PythonCamera" 2>/dev/null; then
    echo "✅ LeRobot Python camera support available"
    
    # Run with Python camera integration
    printf "\n\n" | python -m lerobot.teleoperate \
        --robot.type=so101_follower \
        --robot.port="$FOLLOWER_PORT" \
        --robot.id=lesurgeon_follower_arm \
        --robot.cameras="$PYTHON_CAMERA_CONFIG" \
        --teleop.type=so101_leader \
        --teleop.port="$LEADER_PORT" \
        --teleop.id=lesurgeon_leader_arm \
        --display_data=true
        
else
    echo "⚠️  Python camera support not available in this LeRobot version"
    echo "🔄 Falling back to Method 2: Virtual Camera Bridge"
    echo ""
    
    # Method 2: Use virtual camera bridge as fallback
    echo "🌉 Starting ZED Virtual Camera Bridge..."
    
    # Start the bridge in background
    python src/cameras/zed_virtual_bridge.py --output-device /dev/video20 --mode RGB &
    BRIDGE_PID=$!
    
    # Wait for bridge to initialize
    echo "⏳ Waiting for virtual camera bridge..."
    sleep 5
    
    # Check if virtual device was created
    if [ -e "/dev/video20" ]; then
        echo "✅ Virtual camera bridge ready: /dev/video20"
        
        # Create virtual camera configuration
        VIRTUAL_CAMERA_CONFIG="{
            ${WRIST_CAM_CONFIG}
            \"zed_virtual\": {\"type\": \"opencv\", \"index_or_path\": \"/dev/video20\", \"width\": 1280, \"height\": 720, \"fps\": 30}
        }"
        
        echo "🎮 Starting teleoperation with virtual ZED camera..."
        
        # Run teleoperation with virtual camera
        printf "\n\n" | python -m lerobot.teleoperate \
            --robot.type=so101_follower \
            --robot.port="$FOLLOWER_PORT" \
            --robot.id=lesurgeon_follower_arm \
            --robot.cameras="$VIRTUAL_CAMERA_CONFIG" \
            --teleop.type=so101_leader \
            --teleop.port="$LEADER_PORT" \
            --teleop.id=lesurgeon_leader_arm \
            --display_data=true
            
        # Cleanup virtual bridge
        echo "🧹 Cleaning up virtual camera bridge..."
        kill $BRIDGE_PID 2>/dev/null || true
        
    else
        echo "❌ Virtual camera bridge failed to create /dev/video20"
        echo "Please check v4l2loopback module: sudo modprobe v4l2loopback"
        exit 1
    fi
fi

echo ""
echo "✅ ZED-LeRobot integration completed!"
