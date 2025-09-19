#!/bin/bash
# Port Assignment Verification
# ============================

echo "🔌 USB Port Assignment Verification"
echo "==================================="
echo ""

echo "📋 Current Port Assignment:"
echo "  Follower Robot:  /dev/ttyACM1"
echo "  Leader Teleop:   /dev/ttyACM0"
echo ""

echo "🔍 Available Ports:"
ls -la /dev/ttyACM* 2>/dev/null || echo "  No ttyACM ports found"
echo ""

echo "📊 Port Usage in Scripts:"
echo ""
echo "🎮 Teleoperation (run/teleoperate.sh):"
grep -n "port=" run/teleoperate.sh | sed 's/^/  /'
echo ""

echo "🔧 Calibration Commands:"
echo "  Follower: lesurgeon.sh follower -> /dev/ttyACM1"
echo "  Leader:   lesurgeon.sh leader   -> /dev/ttyACM0"
echo ""

echo "✅ All scripts should now use consistent ports!"
echo ""
echo "🎯 Next Steps:"
echo "1. Try: ./lesurgeon.sh follower"  
echo "2. During calibration, manually move follower arm joints"
echo "3. The system should detect and record the movements"
echo ""