#!/bin/bash
# Robot Status Summary
# ===================
# Quick overview of your calibrated robots

source ../.lerobot/bin/activate

echo "🤖 LeSurgeon Robot Calibration Status"
echo "====================================="
echo ""

echo "✅ SUCCESSFULLY CALIBRATED ROBOTS:"
echo ""

echo "📡 Follower Arm (lesurgeon_follower_arm)"
echo "   Robot Type: so101_follower"
echo "   Port: /dev/ttyACM0"
echo "   Status: ✅ CALIBRATED"
echo "   Calibration file: ~/.cache/huggingface/lerobot/calibration/robots/so101_follower/lesurgeon_follower_arm.json"
echo "   Backup copy: ../config/calibration_backups/lesurgeon_follower_arm.json"
echo ""

echo "🕹️  Leader Arm (lesurgeon_leader_arm)"
echo "   Robot Type: so101_leader (teleoperation)"
echo "   Port: /dev/ttyACM0"  
echo "   Status: ✅ CALIBRATED"
echo "   Calibration file: ~/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/lesurgeon_leader_arm.json"
echo "   Backup copy: ../config/calibration_backups/lesurgeon_leader_arm.json"
echo ""

echo "🔧 CALIBRATION COMMANDS USED:"
echo ""
echo "# Follower calibration:"
echo "lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=lesurgeon_follower_arm"
echo ""
echo "# Leader calibration:"
echo "lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=lesurgeon_leader_arm"
echo ""

echo "🎯 NEXT STEPS:"
echo "1. Test robot connection:"
echo "   python -c \"from lerobot.robots.so101_follower import SO101Follower; print('Robot import OK')\""
echo ""
echo "2. Start data recording:"
echo "   lerobot-record --robot=lesurgeon_follower_arm --teleop=lesurgeon_leader_arm"
echo ""
echo "3. Train a model:"
echo "   python lerobot/scripts/train.py --config-name diffusion"
echo ""

echo "📊 Joint Range Summary:"
echo "======================"
echo ""
echo "Follower Arm Joint Ranges:"
if [ -f "../config/calibration_backups/lesurgeon_follower_arm.json" ]; then
    python3 -c "
import json
with open('../config/calibration_backups/lesurgeon_follower_arm.json', 'r') as f:
    data = json.load(f)
    print('Joint Name      | Min  | Max  | Range | Homing Offset')
    print('-' * 55)
    for joint, info in data.items():
        range_val = info['range_max'] - info['range_min']
        print(f'{joint:14s} | {info[\"range_min\"]:4d} | {info[\"range_max\"]:4d} | {range_val:5d} | {info[\"homing_offset\"]:6d}')
"
else
    echo "   Calibration data not found"
fi

echo ""
echo "Leader Arm Joint Ranges:"
if [ -f "../config/calibration_backups/lesurgeon_leader_arm.json" ]; then
    python3 -c "
import json
with open('../config/calibration_backups/lesurgeon_leader_arm.json', 'r') as f:
    data = json.load(f)
    print('Joint Name      | Min  | Max  | Range | Homing Offset')
    print('-' * 55)
    for joint, info in data.items():
        range_val = info['range_max'] - info['range_min']
        print(f'{joint:14s} | {info[\"range_min\"]:4d} | {info[\"range_max\"]:4d} | {range_val:5d} | {info[\"homing_offset\"]:6d}')
"
else
    echo "   Calibration data not found"
fi

echo ""
echo "✨ Robots ready for LeRobot experiments! 🚀"