# Proper Calibration Guide for Wrist Tracking Issues

## 🎯 Problem: Wrist movements not matching between leader and follower

## 🔧 Solution: Careful Recalibration

### Step 1: Prepare Both Robots
1. **Position both robots** in their center positions
2. **Make sure both robots can move freely** in all directions
3. **Power on both robots** and ensure stable USB connections

### Step 2: Recalibrate Leader Arm (Most Critical)

```bash
./lesurgeon.sh leader
```

**During calibration - IMPORTANT STEPS:**

1. **Initial Position:** Move leader to center, press ENTER

2. **Joint Movement Phase:** Move EACH joint through its FULL range:
   
   **🎯 CRITICAL - Move joints SLOWLY and DELIBERATELY:**
   
   - **Shoulder Pan:** Full left → Full right → Center
   - **Shoulder Lift:** Full up → Full down → Center  
   - **Elbow:** Full extend → Full flex → Center
   - **Wrist Flex:** Full up → Full down → Center
   - **Wrist Roll:** ⚠️ **MOST IMPORTANT** - Full CW rotation → Full CCW rotation → Center
   - **Gripper:** Full close → Full open → Center

3. **Key Points:**
   - Move SLOWLY (don't rush)
   - Go to the ACTUAL limits (feel slight resistance)
   - Hold at each limit for 1-2 seconds
   - Return to center between each joint
   - Press ENTER only after moving ALL joints properly

### Step 3: Recalibrate Follower Arm

```bash  
./lesurgeon.sh follower
```

**Follow the same careful joint movement process**

### Step 4: Test Mapping

After recalibration:
```bash
./lesurgeon.sh teleoperate
```

**Test each joint individually:**
- Move leader shoulder → Check follower shoulder matches
- Move leader wrist → Check follower wrist matches exactly

## 🚨 Common Calibration Mistakes:

1. **Moving too fast** during joint range recording
2. **Not reaching actual joint limits** - go until slight resistance
3. **Skipping joints** - move EVERY joint through FULL range
4. **Not centering between joints** - always return to neutral
5. **Pressing ENTER too early** - make sure you've moved ALL joints

## 📊 Expected Results:

After proper calibration, joint ranges should be similar:
- Leader and follower wrist_flex ranges should be comparable
- Leader wrist_roll should NOT be 0-33040 (that's clearly wrong)
- All joints should have reasonable, bounded ranges

## 🎮 Testing Wrist Movement:

After recalibration, test specifically:
1. Leader wrist up/down → Follower should match
2. Leader wrist rotate CW/CCW → Follower should match
3. Small movements should be proportional
4. Large movements should stay within limits