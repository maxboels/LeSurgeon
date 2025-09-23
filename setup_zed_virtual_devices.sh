#!/usr/bin/env bash

# ZED Virtual Bridge Setup
# Creates virtual devices for LeRobot integration
echo "🌉 ZED Virtual Bridge Setup"
echo "========================================="
echo "This script creates virtual video devices for ZED integration:"
echo "  /dev/video20 - ZED Left RGB"  
echo "  /dev/video21 - ZED Depth (colorized)"
echo ""

# Check if v4l2loopback is available
if ! lsmod | grep -q v4l2loopback; then
    echo "📦 Loading v4l2loopback kernel module..."
    
    # Remove existing v4l2loopback modules
    sudo modprobe -r v4l2loopback 2>/dev/null || true
    
    # Create virtual devices at video20 and video21
    sudo modprobe v4l2loopback \
        devices=2 \
        video_nr=20,21 \
        card_label="ZED_Left_RGB,ZED_Depth" \
        exclusive_caps=1,1
    
    echo "✅ v4l2loopback loaded with virtual devices"
else
    echo "✅ v4l2loopback already loaded"
fi

# Wait for devices to be created
sleep 2

# Verify devices exist
echo ""
echo "🔍 Checking virtual devices..."
if [ -e /dev/video20 ]; then
    echo "✅ /dev/video20 (ZED Left RGB) created"
else
    echo "❌ /dev/video20 not found"
fi

if [ -e /dev/video21 ]; then
    echo "✅ /dev/video21 (ZED Depth) created"
else
    echo "❌ /dev/video21 not found"
fi

echo ""
echo "📋 Current video devices:"
ls -la /dev/video* | grep -E "(video20|video21|video0|video1)" || true

echo ""
echo "🚀 Virtual devices ready for ZED bridge!"
echo "💡 You can now run the Python bridge script."