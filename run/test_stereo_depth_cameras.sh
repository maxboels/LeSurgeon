#!/bin/bash
# Simple 5-Modality Camera Test (No Sudo Required)
# ================================================
# Tests ZED cameras and shows video feeds without creating virtual devices

set -e

echo "📷 Simple 5-Modality Camera Test"
echo "================================"
echo "This will test ZED cameras and show video windows"
echo "No virtual devices created (no sudo required)"
echo ""

# Configuration
BASE_DIR="$HOME/projects/LeSurgeon"
cd "$BASE_DIR"

# Activate LeRobot environment
echo "🔌 Activating LeRobot environment..."
source setup/activate_lerobot.sh

echo ""
echo "🎬 Starting ZED Video Display..."
echo "================================"

echo "📺 This will show 3 video windows:"
echo "   • ZED Left RGB"
echo "   • ZED Right RGB" 
echo "   • ZED Depth Map"
echo ""
echo "⏰ Press 'q' in any window or Ctrl+C to stop"
echo ""

# Run the video display system
python debug/ultimate_zed_display.py --no-virtual