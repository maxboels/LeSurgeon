#!/usr/bin/env python3
"""
ZED Live Multi-Modal Viewer
===========================
Live viewer for ZED 2i camera showing all modalities in separate windows:
- Left RGB camera view
- Right RGB camera view  
- Depth map (20-60cm surgical range)
- Confidence map

Uses our optimized ZED SDK configuration with NEURAL_PLUS depth mode.
"""

import sys
import cv2
import numpy as np
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pyzed.sl as sl
    ZED_SDK_AVAILABLE = True
except ImportError:
    ZED_SDK_AVAILABLE = False
    print("❌ ZED SDK not available. Please install first.")
    
# Import our camera after checking ZED SDK
if ZED_SDK_AVAILABLE:
    from src.cameras.zed_sdk_camera import ZEDSDKCamera

class ZEDLiveViewer:
    """Live viewer for all ZED modalities"""
    
    def __init__(self):
        self.zed_camera = None
        self.is_running = False
        
        # Data containers for additional measures
        self.confidence_map = sl.Mat()
        
    def initialize_camera(self):
        """Initialize ZED camera with surgical settings"""
        print("🔌 Initializing ZED 2i with surgical configuration...")
        
        self.zed_camera = ZEDSDKCamera(
            resolution="HD720",
            depth_mode="NEURAL_PLUS",  # Best quality for surgery
            fps=30
        )
        
        if not self.zed_camera.connect():
            print("❌ Failed to connect ZED camera")
            return False
            
        print("✅ ZED camera initialized with:")
        print("  - Range: 20cm - 50cm (focused surgical workspace)")
        print("  - Mode: NEURAL_PLUS (highest quality)")
        print("  - Confidence: 50% threshold")
        print("  - Resolution: HD720 (1280×720)")
        return True
    
    def process_depth_for_display(self, depth_mm):
        """Convert depth to surgical range visualization"""
        # Clamp to surgical range (20-50cm)
        depth_clamped = np.clip(depth_mm, 200, 500)
        
        # Create mask for valid depths
        valid_mask = (depth_mm > 200) & (depth_mm < 500) & np.isfinite(depth_mm)
        
        # Normalize to 0-255 for display
        depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
        if np.any(valid_mask):
            valid_depths = depth_clamped[valid_mask]
            normalized_valid = ((valid_depths - 200) / (500 - 200) * 255).astype(np.uint8)
            depth_normalized[valid_mask] = normalized_valid
        
        # Apply colormap for better visualization - JET gives better color range for surgical work
        depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        
        # Add surgical range info
        cv2.putText(depth_colored, "Surgical Range: 20-50cm", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(depth_colored, "NEURAL_PLUS Mode", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return depth_colored
    
    def get_confidence_map(self):
        """Get confidence map from ZED camera"""
        if not self.zed_camera.is_connected:
            return None
            
        try:
            if self.zed_camera.zed.retrieve_measure(self.confidence_map, sl.MEASURE.CONFIDENCE) == sl.ERROR_CODE.SUCCESS:
                confidence_np = self.confidence_map.get_data()
                # Convert to 0-255 range for display
                confidence_display = (confidence_np * 255).astype(np.uint8)
                # Use PLASMA colormap for better confidence visualization
                confidence_colored = cv2.applyColorMap(confidence_display, cv2.COLORMAP_PLASMA)
                
                # Add confidence info
                cv2.putText(confidence_colored, "Confidence Map", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(confidence_colored, "Threshold: 50%", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                return confidence_colored
        except Exception as e:
            print(f"❌ Confidence map error: {e}")
            
        return None
    
    def add_frame_info(self, frame, title, additional_info=""):
        """Add title and info to frame"""
        # Add title
        cv2.putText(frame, title, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Add additional info
        if additional_info:
            cv2.putText(frame, additional_info, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add timestamp
        cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def run_live_viewer(self):
        """Run the live viewer with separate windows"""
        print("🎥 Starting ZED Live Multi-Modal Viewer")
        print("=" * 60)
        print("📊 You will see 4 separate windows:")
        print("  📷 ZED Left RGB - Left eye camera view")
        print("  📷 ZED Right RGB - Right eye camera view") 
        print("  🔍 ZED Depth - Neural depth map (20-50cm)")
        print("  🎯 ZED Confidence - Depth confidence map")
        print("")
        print("🎮 Controls:")
        print("  - Press 'q' in any window to quit")
        print("  - Press 's' to save screenshots")
        print("  - Press ESC to exit")
        print("=" * 60)
        
        self.is_running = True
        frame_count = 0
        
        try:
            while self.is_running:
                # Capture all modalities
                data = self.zed_camera.capture_all_modalities()
                
                if not data:
                    print("⚠️  No data from ZED camera")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Process and display Left RGB
                if 'left_rgb' in data:
                    left_frame = data['left_rgb'].copy()
                    left_frame = self.add_frame_info(left_frame, "ZED Left RGB", 
                                                   f"Frame: {frame_count} | 20-50cm Range")
                    cv2.imshow("ZED Left RGB", left_frame)
                
                # Process and display Right RGB  
                if 'right_rgb' in data:
                    right_frame = data['right_rgb'].copy()
                    right_frame = self.add_frame_info(right_frame, "ZED Right RGB", 
                                                    f"Frame: {frame_count} | 20-50cm Range")
                    cv2.imshow("ZED Right RGB", right_frame)
                
                # Process and display Depth
                if 'depth' in data:
                    depth_frame = self.process_depth_for_display(data['depth'])
                    depth_frame = self.add_frame_info(depth_frame, "ZED Depth (NEURAL_PLUS)", 
                                                    f"Frame: {frame_count} | Surgical Range")
                    cv2.imshow("ZED Depth", depth_frame)
                
                # Get and display Confidence Map
                confidence_frame = self.get_confidence_map()
                if confidence_frame is not None:
                    confidence_frame = self.add_frame_info(confidence_frame, "ZED Confidence", 
                                                         f"Frame: {frame_count} | 50% Threshold")
                    cv2.imshow("ZED Confidence", confidence_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    print("🛑 Stopping live viewer...")
                    break
                elif key == ord('s'):  # Save screenshots
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    if 'left_rgb' in data:
                        cv2.imwrite(f"zed_left_{timestamp}.png", data['left_rgb'])
                    if 'right_rgb' in data:
                        cv2.imwrite(f"zed_right_{timestamp}.png", data['right_rgb'])
                    if 'depth' in data:
                        cv2.imwrite(f"zed_depth_{timestamp}.png", depth_frame)
                    if confidence_frame is not None:
                        cv2.imwrite(f"zed_confidence_{timestamp}.png", confidence_frame)
                    print(f"📸 Screenshots saved with timestamp {timestamp}")
                
                # Show stats every 30 frames
                if frame_count % 30 == 0:
                    print(f"📊 Frame {frame_count} | All modalities active | 20-50cm surgical range")
                
        except KeyboardInterrupt:
            print("\\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ Error during live viewing: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        self.is_running = False
        cv2.destroyAllWindows()
        
        if self.zed_camera:
            self.zed_camera.disconnect()
        
        print("✅ Cleanup completed")

def main():
    """Main function"""
    print("🔬 ZED 2i Live Multi-Modal Viewer for Surgical Robotics")
    print("=" * 70)
    
    if not ZED_SDK_AVAILABLE:
        print("❌ ZED SDK not available")
        print("Please install ZED SDK first.")
        return False
    
    viewer = ZEDLiveViewer()
    
    # Initialize camera
    if not viewer.initialize_camera():
        return False
    
    # Run live viewer
    viewer.run_live_viewer()
    
    print("🎉 Live viewer session completed!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)