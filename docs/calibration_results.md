# Robot Calibration Results - September 19, 2025

## ✅ Successfully Calibrated Robots

Both robots have been calibrated and the calibration data has been automatically saved by LeRobot.

### Follower Arm (`lesurgeon_follower_arm`)
**Calibrated:** ✅ SUCCESSFUL  
**File location:** `/home/maxboels/.cache/huggingface/lerobot/calibration/robots/so101_follower/lesurgeon_follower_arm.json`

**Joint Range Values:**
```
NAME            |    MIN |    POS |    MAX
shoulder_pan    |    735 |   2027 |   3427
shoulder_lift   |    807 |    814 |   3235
elbow_flex      |    879 |   3096 |   3101
wrist_flex      |    840 |   2858 |   3187
wrist_roll      |    144 |   2077 |   3971
gripper         |   1830 |   1850 |   3340
```

### Leader Arm (`lesurgeon_leader_arm`)
**Calibrated:** ✅ SUCCESSFUL  
**File location:** `/home/maxboels/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/lesurgeon_leader_arm.json`

**Joint Range Values:**
```
NAME            |    MIN |    POS |    MAX
shoulder_pan    |    807 |   2055 |   3498
shoulder_lift   |    889 |    898 |   3302
elbow_flex      |   2044 |   4266 |   4268
wrist_flex      |    861 |    871 |   2916
wrist_roll      |      0 |   1702 |  33040
gripper         |    825 |   2075 |   2092
```

## 📁 Calibration File Locations

LeRobot automatically saves calibration data in the Hugging Face cache directory:

- **Follower calibration:** `~/.cache/huggingface/lerobot/calibration/robots/so101_follower/lesurgeon_follower_arm.json`
- **Leader calibration:** `~/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/lesurgeon_leader_arm.json`

## 🎯 Usage

These calibration files will be automatically loaded when you use your robot IDs:
- `lesurgeon_follower_arm` - for the follower robot
- `lesurgeon_leader_arm` - for the leader/teleoperator robot

## 🔧 Troubleshooting Notes

The leader arm calibration initially failed several times with "Magnitude exceeds 2047" errors, but succeeded after manually positioning the joints closer to center. Key lesson: **always position joints near center before calibration**.

## ✨ Next Steps

Your robots are now ready for:
- Data recording sessions
- Training runs
- Teleoperation tasks
- Any LeRobot experiments

The calibration ensures accurate joint position mapping and proper range limits for safe operation.