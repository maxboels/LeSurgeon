#!/usr/bin/env python3
"""
ZED Display Add-on for LeRobot Teleoperation
============================================
Run this in parallel with your existing teleoperation to get ZED depth visualization.
This doesn't interfere with LeRobot - just provides additional ZED camera views.
"""

import sys
import cv2
import numpy as np
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_opencv_bridge import ZEDOpenCVBridge

class ZEDDisplayAddon:
    """Additional ZED camera display for teleoperation"""
    
    def __init__(self):
        self.zed_camera = None
        self.running = False
        self.frame_cache = {}
        self.cache_lock = threading.Lock()
        
        print("🎥 ZED Display Add-on for LeRobot Teleoperation")
        print("=" * 60)
        print("This provides additional ZED camera views alongside your")
        print("existing LeRobot teleoperation session.")
        print("")
    
    def initialize_cameras(self):
        """Initialize single ZED camera for all modalities"""
        print("📷 Initializing ZED camera...")
        
        try:
            # Import ZED SDK camera directly
            from src.cameras.zed_sdk_camera import ZEDSDKCamera
            
            self.zed_camera = ZEDSDKCamera(
                resolution="HD720",
                depth_mode="NEURAL_PLUS",
                fps=30
            )
            
            if self.zed_camera.connect():
                print("✅ ZED camera connected - all modalities available")
                print("  📷 ZED Left RGB")
                print("  📷 ZED Right RGB") 
                print("  🔍 ZED Depth (20-50cm surgical range)")
                return True
            else:
                print("❌ Failed to connect ZED camera")
                return False
                
        except Exception as e:
            print(f"❌ ZED camera initialization error: {e}")
            return False
    
    def create_display_frame(self):
        """Create combined display frame from ZED camera"""
        if not self.zed_camera:
            return None
        
        try:
            # Capture all modalities from single ZED camera
            data = self.zed_camera.capture_all_modalities()
            if not data:
                return None
            
            frames = {}
            
            # Process left RGB
            if 'left_rgb' in data:
                left_frame = data['left_rgb']
                if left_frame.shape[2] == 4:  # RGBA -> RGB
                    left_frame = left_frame[:, :, :3]
                # Convert RGB to BGR for OpenCV display
                left_frame = cv2.cvtColor(left_frame, cv2.COLOR_RGB2BGR)
                left_frame = cv2.resize(left_frame, (640, 480))
                
                # Add title
                cv2.putText(left_frame, "ZED Left RGB", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                frames["ZED Left RGB"] = left_frame
            
            # Process right RGB
            if 'right_rgb' in data:
                right_frame = data['right_rgb']
                if right_frame.shape[2] == 4:  # RGBA -> RGB
                    right_frame = right_frame[:, :, :3]
                # Convert RGB to BGR for OpenCV display
                right_frame = cv2.cvtColor(right_frame, cv2.COLOR_RGB2BGR)
                right_frame = cv2.resize(right_frame, (640, 480))
                
                # Add title
                cv2.putText(right_frame, "ZED Right RGB", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                frames["ZED Right RGB"] = right_frame
            
            # Process depth
            if 'depth' in data:
                depth_mm = data['depth']
                
                # Process depth for surgical range (20-50cm)
                depth_clamped = np.clip(depth_mm, 200, 500)
                valid_mask = (depth_mm >= 200) & (depth_mm <= 500) & np.isfinite(depth_mm)
                
                depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
                if np.any(valid_mask):
                    valid_depths = depth_clamped[valid_mask]
                    normalized_valid = ((valid_depths - 200) / 300 * 255).astype(np.uint8)
                    depth_normalized[valid_mask] = normalized_valid
                
                # Apply colormap
                depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
                depth_frame = cv2.resize(depth_colored, (640, 480))
                
                # Add title and surgical info
                cv2.putText(depth_frame, "ZED Depth (20-50cm)", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Add depth statistics
                if np.any(valid_mask):
                    valid_pixels = np.sum(valid_mask)
                    total_pixels = depth_mm.size
                    coverage = (valid_pixels / total_pixels) * 100
                    cv2.putText(depth_frame, f"Coverage: {coverage:.1f}%", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                frames["ZED Depth"] = depth_frame
            
            # Add timestamp to all frames
            timestamp = time.strftime("%H:%M:%S")
            for frame in frames.values():
                cv2.putText(frame, timestamp, (10, frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
        except Exception as e:
            print(f"❌ Error processing ZED data: {e}")
            return None
        
        if not frames:
            return None
        
        # Arrange frames in surgical layout
        frame_list = list(frames.values())
        
        if len(frame_list) == 1:
            return frame_list[0]
        elif len(frame_list) == 2:
            return np.hstack(frame_list)
        elif len(frame_list) >= 3:
            # Surgical layout: Left and Right on top, Depth on bottom
            if "ZED Left RGB" in frames and "ZED Right RGB" in frames and "ZED Depth" in frames:
                top_row = np.hstack([frames["ZED Left RGB"], frames["ZED Right RGB"]])
                depth_frame = frames["ZED Depth"]
                
                # Center the depth frame under the stereo pair
                padding = (top_row.shape[1] - depth_frame.shape[1]) // 2
                if padding > 0:
                    pad_left = np.zeros((depth_frame.shape[0], padding, 3), dtype=np.uint8)
                    pad_right = np.zeros((depth_frame.shape[0], padding, 3), dtype=np.uint8)
                    bottom_row = np.hstack([pad_left, depth_frame, pad_right])
                else:
                    bottom_row = depth_frame
                
                return np.vstack([top_row, bottom_row])
            else:
                # Fallback arrangement
                return np.hstack(frame_list[:2]) if len(frame_list) >= 2 else frame_list[0]
        
        return None
    
    def run_display(self):
        """Main display loop"""
        print("🎬 Starting ZED display...")
        print("")
        print("🎮 Controls:")
        print("  - Press 'q' or ESC to quit")
        print("  - Press 's' to save screenshot")
        print("  - This runs alongside your LeRobot teleoperation")
        print("")
        print("📊 Camera Views:")
        print("  - ZED Left RGB")
        print("  - ZED Right RGB") 
        print("  - ZED Depth (20-50cm surgical range)")
        print("")
        
        self.running = True
        frame_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                # Create display frame
                display_frame = self.create_display_frame()
                
                if display_frame is not None:
                    # Add overall info
                    frame_count += 1
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    info_text = f"ZED Add-on | Frame: {frame_count} | FPS: {fps:.1f}"
                    cv2.putText(display_frame, info_text, (10, display_frame.shape[0] - 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    
                    # Show display
                    cv2.imshow("ZED Surgical Cameras (Add-on)", display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    print("🛑 Quit requested")
                    break
                elif key == ord('s'):  # Save screenshot
                    if display_frame is not None:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"zed_surgical_view_{timestamp}.png"
                        cv2.imwrite(filename, display_frame)
                        print(f"📸 Screenshot saved: {filename}")
                
                time.sleep(1/30)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up ZED add-on...")
        self.running = False
        
        # Release ZED camera
        if self.zed_camera:
            try:
                self.zed_camera.disconnect()
                print("🔌 ZED camera released")
            except Exception as e:
                print(f"❌ Error releasing ZED camera: {e}")
        
        cv2.destroyAllWindows()
        print("✅ ZED add-on cleanup complete")
    
    def run(self):
        """Main entry point"""
        if not self.initialize_cameras():
            print("❌ ZED camera not available")
            return False
        
        print("🚀 ZED Display Add-on ready!")
        print("💡 Now run your normal LeRobot teleoperation in another terminal:")
        print("   ./lesurgeon.sh teleop-cam")
        print("")
        print("⏳ Starting display in 3 seconds...")
        time.sleep(3)
        
        self.run_display()
        return True


def main():
    """Main function"""
    print("🎥 ZED Display Add-on for LeRobot")
    print("=" * 50)
    print("This provides additional ZED camera views that run")
    print("alongside your existing LeRobot teleoperation.")
    print("")
    print("💡 Usage:")
    print("  1. Start this script")
    print("  2. In another terminal: ./lesurgeon.sh teleop-cam") 
    print("  3. You'll get both LeRobot UI + ZED surgical views")
    print("")
    
    addon = ZEDDisplayAddon()
    success = addon.run()
    
    if success:
        print("🎉 ZED add-on session completed!")
    else:
        print("❌ ZED add-on failed to start")
    
    return success


if __name__ == "__main__":
    main()