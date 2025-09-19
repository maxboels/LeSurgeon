#!/usr/bin/env python3
"""
Simple Motor Position Reader
===========================
This script attempts to read motor positions using the same approach as calibration.
"""

import traceback

def diagnose_so101_leader():
    print("🔧 SO101 Leader Position Diagnosis")
    print("=" * 40)
    
    try:
        # Import and create the same setup as calibration
        from lerobot.teleoperators.so101_leader.so101_leader import SO101Leader
        from dataclasses import dataclass
        from pathlib import Path
        
        # Create config similar to calibration
        @dataclass
        class TeleopConfig:
            calibration_dir: Path = None
            id: str = "diagnostic_leader"
            port: str = "/dev/ttyACM0"
            use_degrees: bool = False
        
        config = TeleopConfig()
        
        print(f"Connecting to SO101 Leader on {config.port}...")
        
        # This should match how calibration creates the leader
        leader = SO101Leader(**config.__dict__)
        
        print("✅ Connected successfully!")
        print()
        
        # Get motor positions
        print("📊 Reading motor positions:")
        print("-" * 60)
        print("Motor ID | Position | Magnitude | Status")
        print("-" * 60)
        
        problematic_motors = []
        
        # Read positions from all motors
        bus = leader.bus
        for motor_id in sorted(bus.motors.keys()):
            try:
                position = bus.read("Present_Position", motor_id)
                magnitude = abs(position)
                
                if magnitude > 2047:
                    status = "⚠️  PROBLEM (>2047)"
                    problematic_motors.append((motor_id, position, magnitude))
                elif magnitude > 1800:
                    status = "⚡ HIGH (close to limit)"
                else:
                    status = "✅ OK"
                    
                print(f"   {motor_id:2d}    |  {position:6d}  |   {magnitude:4d}    | {status}")
                
            except Exception as e:
                print(f"   {motor_id:2d}    |  ERROR   |    N/A    | ❌ {str(e)[:20]}...")
                
        print("-" * 60)
        print()
        
        # Analysis
        if problematic_motors:
            print("❌ FOUND PROBLEMATIC MOTOR(S):")
            for motor_id, position, magnitude in problematic_motors:
                motor_names = {
                    1: "Base rotation",
                    2: "Shoulder", 
                    3: "Elbow",
                    4: "Wrist rotation",
                    5: "Wrist pitch", 
                    6: "Gripper"
                }
                motor_name = motor_names.get(motor_id, f"Motor {motor_id}")
                print(f"  🎯 Motor {motor_id} ({motor_name}): position={position}, magnitude={magnitude}")
                print(f"      This motor needs to be moved closer to center position!")
                
            print("\n🛠️  SOLUTION:")
            print("   Manually move the problematic motor(s) to roughly center position")
            print("   Each joint should be approximately in the middle of its range of motion")
            print("   Then try calibration again")
                
        else:
            print("✅ All motors are within acceptable range!")
            print("   Try running calibration again - the issue might be resolved")
        
        # Disconnect
        leader.disconnect()
        print("\n🔌 Disconnected")
        
        return problematic_motors
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nFull error traceback:")
        traceback.print_exc()
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Make sure robot is powered on")
        print(f"2. Check USB connection to /dev/ttyACM0") 
        print(f"3. Try unplugging and reconnecting USB")
        return None

if __name__ == "__main__":
    result = diagnose_so101_leader()
    if result is None:
        print("❌ Could not diagnose - connection issue")
    elif result:
        print(f"\n🚨 Found {len(result)} motor(s) that need adjustment")
    else:
        print(f"\n🎉 Ready for calibration!")