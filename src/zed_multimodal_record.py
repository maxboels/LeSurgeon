#!/usr/bin/env python3
"""
ZED Multi-Modal Recording Script
===============================
Custom recording script that handles ZED multi-modal cameras and
integrates with LeRobot recording system.
"""

import sys
import os
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    """
    For now, this acts as a pass-through to standard LeRobot recording.
    In the future, we'll add ZED multi-modal camera handling here.
    """
    print("🌐 ZED Multi-Modal Recording")
    print("Note: Currently using standard LeRobot recording with ZED stereo configuration")
    print("ZED multi-modal features (separate L/R + depth + pointcloud) will be added in next update")
    
    # Import and run standard LeRobot recording
    from lerobot.record import main as lerobot_record_main
    
    # Pass through all command line arguments
    lerobot_record_main()


if __name__ == "__main__":
    main()