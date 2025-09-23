#!/usr/bin/env python3
"""
LeSurgeon Camera System Test
===========================
Test script for the reorganized camera modules.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all camera modules can be imported correctly"""
    print("🧪 Testing Camera Module Imports")
    print("=" * 50)
    
    try:
        from src.cameras import ZEDMultiModalCamera, LeRobotZEDCamera, MultiModalCollector
        print("✅ Core camera modules imported successfully")
        
        # Test individual imports
        from src.cameras.zed_multimodal_camera import ZEDMultiModalCamera as ZMC
        from src.cameras.lerobot_zed_integration import LeRobotZEDCamera as LRZC
        from src.cameras.multimodal_collector import MultiModalCollector as MMC
        
        print("✅ Individual camera modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_camera_creation():
    """Test camera object creation without connecting"""
    print(f"\n🎯 Testing Camera Object Creation")
    print("=" * 50)
    
    try:
        from src.cameras import ZEDMultiModalCamera, LeRobotZEDCamera, MultiModalCollector
        
        # Test ZED multi-modal camera creation
        zed_camera = ZEDMultiModalCamera(
            width=2560, height=720, fps=30,
            compute_depth=True, compute_pointcloud=True
        )
        print("✅ ZEDMultiModalCamera created successfully")
        
        # Test LeRobot ZED camera creation
        lerobot_camera = LeRobotZEDCamera(
            resolution='hd',
            include_depth=True,
            include_pointcloud=True
        )
        print("✅ LeRobotZEDCamera created successfully")
        
        # Test Multi-modal camera collector creation
        collector = MultiModalCollector(
            output_dir="outputs/test_multimodal_data",
            zed_resolution="hd",
            save_pointclouds=True,
            save_depth_maps=True
        )
        print("✅ MultiModalCollector created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Camera creation error: {e}")
        return False

def show_project_structure():
    """Show the new project structure"""
    print(f"\n📁 New Project Structure")
    print("=" * 50)
    
    structure = """
LeSurgeon/
├── src/                           # Source code (NEW!)
│   ├── __init__.py               # Main package init
│   ├── cameras/                  # Camera systems
│   │   ├── __init__.py          
│   │   ├── zed_multimodal_camera.py      # ZED stereo + depth + 3D
│   │   ├── lerobot_zed_integration.py    # LeRobot integration
│   │   └── multimodal_collector.py       # Multi-modal data collection
│   └── utils/                    # Utilities
│       ├── __init__.py
│       └── detect_cameras.sh     # Smart camera detection
├── debug/                        # Debug tools (reduced scope)
│   ├── test_zed_camera.py       # Basic camera testing
│   ├── explore_zed_depth.py     # Depth exploration
│   └── [other debug tools...]
├── run/                          # Operation scripts (updated imports)
│   ├── record_data.sh           # Now uses src/utils/detect_cameras.sh
│   ├── run_inference.sh         # Now uses src/utils/detect_cameras.sh
│   └── [other scripts...]
└── [other directories...]

Benefits of this structure:
✅ Clear separation: src/ = production code, debug/ = development tools
✅ Proper Python packaging with __init__.py files
✅ Logical organization: cameras/, utils/, etc.
✅ Easy imports: from src.cameras import ZEDMultiModalCamera
✅ Scalable for future modules (src/robots/, src/training/, etc.)
"""
    print(structure)

def main():
    """Main test function"""
    print("🔄 LeSurgeon Camera System Reorganization Test")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(test_imports())
    
    # Test camera creation
    results.append(test_camera_creation())
    
    # Show new structure
    show_project_structure()
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed ({passed}/{total})!")
        print(f"✅ Camera system reorganization successful")
        print(f"\n🚀 Ready for enhanced surgical robotics!")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print(f"Please check the errors above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)