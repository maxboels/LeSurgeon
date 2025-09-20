#!/bin/bash
# Dynamic ARM Calibration Script
# Automatically detects the correct ports for each arm

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🔧 Starting ARM calibration with dynamic port detection..."
echo ""

# Detect ports
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "📋 Calibration Plan:"
echo "  - Follower arm: $FOLLOWER_PORT (serial: 58FA101278)"
echo "  - Leader arm:   $LEADER_PORT (serial: 5A46085090)"
echo ""

# Follower
echo "🤖 Calibrating Follower Arm..."
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm

echo ""

# Leader
echo "🎮 Calibrating Leader Arm..."
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm