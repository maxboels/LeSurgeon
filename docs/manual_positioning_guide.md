# Manual Robot Positioning Guide

## Current Issue
Calibration failing with: `ValueError: Magnitude 2506 exceeds 2047 (max for sign_bit_index=11)`

This means one of the robot joints is positioned too far from its center position.

## Solution: Manual Positioning

Before running calibration, manually move **ALL** robot joints to their approximate center positions:

### SO101 Leader Arm Joints to Center:

1. **Shoulder/Base Joint**: Rotate to face forward (0° position)
2. **Upper Arm Joint**: Position upper arm roughly horizontal 
3. **Forearm Joint**: Position forearm at roughly 90° to upper arm
4. **Wrist Pitch**: Position wrist straight (neutral)
5. **Wrist Roll**: Position wrist at center rotation
6. **Gripper**: Position gripper half-open

### Visual Guide:
```
    Center Position Goal:
    
         Shoulder
         |
    Upper Arm (horizontal)
         |
    Forearm (90° down)
         |
    Wrist (straight)
         |
    Gripper (half-open)
```

### After Manual Positioning:
1. Make sure all joints can move freely in both directions
2. Verify no joint is at its extreme limit
3. Run the calibration command again

## Calibration Command:
```bash
source .lerobot/bin/activate
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=lesurgeon_leader_arm
```

## Tips:
- Move joints gently and slowly
- If any joint feels stuck or at limit, move it away from the limit
- The robot should be able to move in all directions from the center position
- You don't need to be perfectly precise - just avoid extreme positions