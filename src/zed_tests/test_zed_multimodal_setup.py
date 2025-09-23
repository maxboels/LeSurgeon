#!/usr/bin/env python3
"""
ZED Multi-Modal Setup Test
===========================
Test the complete ZED multi-modal camera setup for LeRobot integration.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test all module imports"""
    print("🧪 Testing Module Imports")
    print("=" * 50)
    
    try:
        from src.cameras.zed_multimodal_camera import ZEDMultiModalCamera as ZEDCamera
        print("✅ ZED MultiModal Camera imported")
        
        from src.cameras.lerobot_zed_multimodal import ZEDMultiModalCamera as ZEDLRCamera
        print("✅ ZED LeRobot Camera imported")
        
        from src.cameras.zed_camera_factory import create_zed_multimodal_camera, register_zed_cameras
        print("✅ ZED Camera Factory imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_camera_factory():
    """Test the camera factory system"""
    print("\n🏭 Testing Camera Factory")
    print("=" * 50)
    
    try:
        from src.cameras.zed_camera_factory import parse_camera_config_string
        
        # Test configuration similar to what detect_cameras.sh would generate
        config_string = """{ 
            wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, 
            zed_left: {type: zed_multimodal, eye: left, width: 2560, height: 720, fps: 30}, 
            zed_right: {type: zed_multimodal, eye: right, width: 2560, height: 720, fps: 30},
            zed_depth: {type: zed_multimodal, modality: depth, width: 2560, height: 720, fps: 30},
            zed_pointcloud: {type: zed_multimodal, modality: pointcloud, width: 2560, height: 720, fps: 30}
        }"""
        
        print("📋 Parsing camera configuration...")
        camera_configs = parse_camera_config_string(config_string)
        
        print(f"✅ Parsed {len(camera_configs)} camera configurations:")
        for name, config in camera_configs.items():
            print(f"   {name}: type={config.get('type', 'unknown')}")
            if 'eye' in config:
                print(f"      -> ZED eye: {config['eye']}")
            elif 'modality' in config:
                print(f"      -> ZED modality: {config['modality']}")
        
        return len(camera_configs) == 5
        
    except Exception as e:
        print(f"❌ Camera factory test error: {e}")
        return False


def test_camera_detection():
    """Test camera detection script"""
    print("\n🔍 Testing Camera Detection")
    print("=" * 50)
    
    try:
        import subprocess
        
        # Test camera detection script
        result = subprocess.run([
            'bash', '-c', 'cd /home/maxboels/projects/LeSurgeon && bash src/utils/detect_cameras.sh'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Camera detection script runs successfully")
            print("Output:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print(f"❌ Camera detection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Camera detection test error: {e}")
        return False


def test_recording_script_syntax():
    """Test that the recording script has valid syntax"""
    print("\n📝 Testing Recording Script")
    print("=" * 50)
    
    try:
        # Test that the Python recording script can be imported
        sys.path.insert(0, project_root)
        
        # Just test that it can be imported without running
        import src.zed_multimodal_record
        print("✅ ZED multi-modal recording script imports successfully")
        
        # Test bash script syntax
        import subprocess
        result = subprocess.run([
            'bash', '-n', '/home/maxboels/projects/LeSurgeon/run/record_data.sh'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Recording script has valid bash syntax")
            return True
        else:
            print(f"❌ Recording script syntax error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Recording script test error: {e}")
        return False


def simulate_recording_command():
    """Simulate what the recording command would look like"""
    print("\n🎬 Simulating Recording Command")
    print("=" * 50)
    
    # Simulate camera detection
    camera_config = """{ 
        wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, 
        zed_left: {type: zed_multimodal, eye: left}, 
        zed_right: {type: zed_multimodal, eye: right}, 
        zed_depth: {type: zed_multimodal, modality: depth}, 
        zed_pointcloud: {type: zed_multimodal, modality: pointcloud}
    }"""
    
    print("🎯 Expected recording command with ZED multi-modal:")
    print("python src/zed_multimodal_record.py \\")
    print("    --robot.type=so101_follower \\")
    print("    --robot.port=/dev/ttyUSB1 \\") 
    print("    --robot.id=lesurgeon_follower_arm \\")
    print(f'    --robot.cameras="{camera_config}" \\')
    print("    --teleop.type=so101_leader \\")
    print("    --teleop.port=/dev/ttyUSB0 \\")
    print("    --teleop.id=lesurgeon_leader_arm \\")
    print("    --display_data=true")
    print()
    
    print("📊 Expected modalities in LeRobot interface:")
    print("   1. observation.images.wrist - USB wrist camera (1280x720)")
    print("   2. observation.images.zed_left - ZED left eye RGB (1280x720)")
    print("   3. observation.images.zed_right - ZED right eye RGB (1280x720)")
    print("   4. observation.depth.zed_depth - ZED depth map (1280x720)")  
    print("   5. observation.pointcloud.zed_pointcloud - ZED 3D points (Nx6)")
    
    return True


def main():
    """Run all tests"""
    print("🔄 ZED Multi-Modal Setup Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Camera Factory", test_camera_factory), 
        ("Camera Detection", test_camera_detection),
        ("Recording Script", test_recording_script_syntax),
        ("Command Simulation", simulate_recording_command)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ZED multi-modal setup is ready.")
        print("\n🚀 Next steps:")
        print("   1. Connect your hardware: wrist USB camera + ZED 2 stereo")
        print("   2. Run: ./lesurgeon.sh record --zed-multimodal")
        print("   3. You should see all 5 modalities in the LeRobot recording interface")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Please fix issues before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)