# Dynamic Port Detection Implementation
## September 20, 2025

### 🎯 **Problem Solved**
Previously, the LeSurgeon scripts used hardcoded port assignments (`/dev/ttyACM0` and `/dev/ttyACM1`) which could change if USB devices were plugged in different orders or after system reboots.

### 🔧 **Solution Implemented**
Created a dynamic port detection system based on unique hardware serial numbers:

- **Leader Arm Serial**: `5A46085090`
- **Follower Arm Serial**: `58FA101278`

### 📁 **New Files Created**

1. **`debug/detect_arm_ports.sh`** - Core port detection utility
   - Scans all `/dev/ttyACM*` devices
   - Matches devices by hardware serial numbers
   - Exports `LEADER_PORT` and `FOLLOWER_PORT` environment variables
   - Can be run standalone or sourced by other scripts

2. **`debug/test_port_detection.sh`** - Test script to verify functionality

### 🔄 **Modified Scripts**

All robot operation scripts now use dynamic port detection:

1. **`config/calibration.sh`** - Robot calibration script
2. **`run/teleoperate.sh`** - Basic teleoperation
3. **`run/teleoperate_auto.sh`** - Auto-confirm teleoperation
4. **`run/teleoperate_with_camera.sh`** - Camera-enabled teleoperation
5. **`lesurgeon.sh`** - Main command interface (all calibration commands)

### 🎯 **Benefits**

- **Robust**: Works regardless of USB enumeration order
- **Reliable**: Survives device unplugging/replugging
- **Automatic**: No manual port configuration needed
- **Backwards Compatible**: Still works with current setup
- **Error Handling**: Clear error messages if devices not found

### 🚀 **Usage**

The system is completely transparent - all existing commands work exactly the same:

```bash
./lesurgeon.sh calibrate
./lesurgeon.sh follower
./lesurgeon.sh leader
./lesurgeon.sh teleoperate
```

### 🔍 **Manual Detection**

To manually check port assignments:
```bash
./debug/detect_arm_ports.sh
```

### 🧪 **Testing**

Run the test suite:
```bash
./debug/test_port_detection.sh
```

### 📊 **Current UGREEN Hub Mapping**

| Device | Serial | Current Port | Hub Position |
|--------|---------|-------------|--------------|
| Leader Arm | 5A46085090 | /dev/ttyACM0 | Port 2 (3-6.2) |
| Follower Arm | 58FA101278 | /dev/ttyACM1 | Port 1 (3-6.1) |

### 🛡️ **Error Handling**

All scripts now include:
- Port detection validation
- Clear error messages for missing devices
- Graceful failure if arms are not connected
- Instructions for troubleshooting connection issues

The system is now completely robust and will work reliably even if the USB topology changes!