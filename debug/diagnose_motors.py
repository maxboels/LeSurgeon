#!/usr/bin/env python3
"""
LeRobot SO101 Motor Diagnostic Script
====================================
This script helps identify which servo motor is causing calibration issues
by reading the current positions of all motors using the motors bus directly.
"""

import sys
from lerobot.motors.feetech import FeetechMotorsBus

def diagnose_motors():
    print("🔧 SO101 Leader Motor Diagnostics")
    print("=" * 40)
    
    try:
        # Connect directly to the motors bus
        print("Connecting to motors bus on /dev/ttyACM0...")
        
        # Create motors bus with SO101 configuration
        from lerobot.motors.feetech.sts3032 import STS3032
        
        # Define motors like in SO101 config
        motors = {}
        for i in range(1, 7):  # Motors 1-6
            motors[i] = STS3032(
                name=f"motor_{i}",
                motor_id=i,
                max_velocity=90,
                max_torque_ratio=0.9,
                homing_offset=0,
                angle_limits=[-180, 180]
            )
        
        bus = FeetechMotorsBus(
            port="/dev/ttyACM0",
            motors=motors
        )
        bus.connect()
        print("✅ Connected successfully!")
        print()
        
        # Read current positions
        print("📊 Reading current motor positions:")
        print("-" * 50)
        print("Motor | Position | Status     | Voltage | Temp")
        print("-" * 50)
        
        problematic_motors = []
        
        for motor_id in bus.motors:
            try:
                # Read present position
                position = bus.read("Present_Position", motor_id)
                
                # Check if position is out of range (magnitude > 2047)
                magnitude = abs(position)
                status = "✅ OK" if magnitude <= 2047 else "⚠️  OUT OF RANGE!"
                
                if magnitude > 2047:
                    problematic_motors.append((motor_id, position, magnitude))
                
                # Read voltage and temperature if possible
                try:
                    voltage = bus.read("Present_Voltage", motor_id)
                    temp = bus.read("Present_Temperature", motor_id)
                    print(f"  {motor_id:2d}  | {position:8d} | {status:10s} | {voltage:6.1f}V | {temp:3d}°C")
                except:
                    print(f"  {motor_id:2d}  | {position:8d} | {status:10s} | N/A     | N/A")
                
            except Exception as e:
                print(f"  {motor_id:2d}  | ERROR    | ❌ {str(e)[:20]}...")
        
        print("-" * 50)
        print()
        
        # Analysis
        print("🔍 Analysis:")
        if problematic_motors:
            print(f"❌ Found {len(problematic_motors)} problematic motor(s):")
            for motor_id, position, magnitude in problematic_motors:
                print(f"   Motor {motor_id}: position={position}, magnitude={magnitude} (max=2047)")
            print()
            print("🛠️  Solution:")
            print("   Manually move the problematic motor(s) closer to center position")
            print("   Each motor should be roughly in the middle of its movement range")
        else:
            print("✅ All motors are within acceptable range")
            print("   The calibration issue might be intermittent or resolved")
        
        return problematic_motors
        
    except Exception as e:
        print(f"❌ Failed to connect or diagnose: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check robot is connected to /dev/ttyACM0")
        print("2. Make sure robot is powered on")
        print("3. Verify no other programs are using the port")
        print("4. Try disconnecting and reconnecting the USB cable")
        return None
        
    finally:
        try:
            bus.disconnect()
            print("\n🔌 Disconnected from robot")
        except:
            pass

if __name__ == "__main__":
    problematic = diagnose_motors()
    
    if problematic:
        print(f"\n🎯 Next steps:")
        print(f"1. Manually adjust motor(s): {', '.join([str(m[0]) for m in problematic])}")
        print(f"2. Run calibration again after positioning")
        sys.exit(1)
    elif problematic is not None:
        print(f"\n🎉 All motors look good! Try calibration again.")
        sys.exit(0)