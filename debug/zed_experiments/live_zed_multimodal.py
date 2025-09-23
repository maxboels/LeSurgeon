#!/usr/bin/env python3
"""
Live ZED SDK Multi-Modal Video Capture
=====================================
Real-time display of all ZED camera modalities:
- Left RGB view
- Right RGB view  
- Depth map (colorized)
- Point cloud visualization

This demonstrates the data quality before LeRobot integration.
Press 'q' to quit, 's' to save sample frames.
"""

import sys
import cv2
import numpy as np
import time
from pathlib import Path

sys.path.append('src')
from cameras.zed_sdk_camera import ZEDSDKCamera

def colorize_depth(depth_map, max_depth_mm=5000):
    """Convert depth map to colorized visualization"""
    # Normalize depth to 0-255 range
    depth_normalized = np.clip(depth_map / max_depth_mm * 255, 0, 255).astype(np.uint8)
    
    # Apply colormap (COLORMAP_JET gives nice blue->red gradient)
    depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
    
    # Set invalid depths (NaN/inf) to black
    invalid_mask = ~np.isfinite(depth_map)
    depth_colored[invalid_mask] = [0, 0, 0]
    
    return depth_colored

def create_pointcloud_top_view(pointcloud, image_size=(400, 400)):
    """Create top-down view of point cloud for visualization"""
    # Extract XYZ coordinates (first 3 channels)
    xyz = pointcloud[:, :, :3]
    
    # Filter valid points (not NaN/inf)
    valid_mask = np.isfinite(xyz).all(axis=2)
    valid_points = xyz[valid_mask]
    
    if len(valid_points) == 0:
        return np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)
    
    # Project to top-down view (X-Z plane, looking down Y axis)
    x_coords = valid_points[:, 0]  # X (left-right)
    z_coords = valid_points[:, 2]  # Z (forward-back)
    
    # Filter reasonable range (e.g., ±3 meters)
    range_limit = 3000  # mm
    in_range = (np.abs(x_coords) < range_limit) & (np.abs(z_coords) < range_limit)
    
    if np.sum(in_range) == 0:
        return np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)
    
    x_filtered = x_coords[in_range]
    z_filtered = z_coords[in_range]
    
    # Convert to image coordinates
    x_img = ((x_filtered + range_limit) / (2 * range_limit) * image_size[1]).astype(int)
    z_img = ((z_filtered + range_limit) / (2 * range_limit) * image_size[0]).astype(int)
    
    # Clip to image bounds
    x_img = np.clip(x_img, 0, image_size[1] - 1)
    z_img = np.clip(z_img, 0, image_size[0] - 1)
    
    # Create top-down view
    top_view = np.zeros((image_size[0], image_size[1], 3), dtype=np.uint8)
    top_view[z_img, x_img] = [0, 255, 0]  # Green points
    
    return top_view

def live_multimodal_capture():
    """Live capture and display of all ZED modalities"""
    print("🎥 Starting Live ZED Multi-Modal Capture")
    print("=" * 50)
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save sample frames")
    print("  - Press 'f' to toggle full resolution")
    print()
    
    try:
        # Initialize ZED camera
        camera = ZEDSDKCamera(
            resolution="HD720",
            depth_mode="NEURAL_LIGHT",  # Faster for real-time
            fps=30
        )
        
        if not camera.connect():
            print("❌ Failed to connect to ZED camera")
            return
        
        print("📷 Camera connected! Starting live capture...")
        print("🔍 Window layout: Top-left=Left RGB, Top-right=Right RGB")
        print("🔍 Window layout: Bottom-left=Depth, Bottom-right=Point Cloud Top View")
        print()
        
        # Performance tracking
        frame_count = 0
        start_time = time.time()
        
        while True:
            # Capture frame
            data = camera.capture_all_modalities()
            
            if not data:
                print("⚠️  No data received")
                continue
            
            # Get individual modalities
            left_rgb = data['left_rgb']
            right_rgb = data['right_rgb'] 
            depth_map = data['depth']
            pointcloud = data['point_cloud']
            
            # Convert BGR for OpenCV display
            left_bgr = cv2.cvtColor(left_rgb, cv2.COLOR_RGB2BGR)
            right_bgr = cv2.cvtColor(right_rgb, cv2.COLOR_RGB2BGR)
            
            # Colorize depth map
            depth_colored = colorize_depth(depth_map)
            
            # Create point cloud top view
            pc_top_view = create_pointcloud_top_view(pointcloud)
            
            # Resize for display (half size for better layout)
            display_size = (640, 360)  # Half of HD720
            left_display = cv2.resize(left_bgr, display_size)
            right_display = cv2.resize(right_bgr, display_size)
            depth_display = cv2.resize(depth_colored, display_size)
            pc_display = cv2.resize(pc_top_view, display_size)
            
            # Add labels
            cv2.putText(left_display, "LEFT RGB", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(right_display, "RIGHT RGB", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(depth_display, "DEPTH (NEURAL)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(pc_display, "POINTCLOUD TOP", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Performance info
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Add FPS to each view
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(left_display, fps_text, (10, display_size[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Add depth statistics
            valid_depth = np.count_nonzero(~np.isnan(depth_map))
            total_pixels = depth_map.size
            depth_percentage = valid_depth / total_pixels * 100
            depth_stats = f"Valid: {depth_percentage:.1f}%"
            cv2.putText(depth_display, depth_stats, (10, display_size[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Create combined display (2x2 grid)
            top_row = np.hstack([left_display, right_display])
            bottom_row = np.hstack([depth_display, pc_display])
            combined = np.vstack([top_row, bottom_row])
            
            # Show combined view
            cv2.imshow("ZED SDK Multi-Modal Live View", combined)
            
            # Handle keypresses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("🛑 Quit requested")
                break
            elif key == ord('s'):
                # Save sample frames
                timestamp = int(time.time())
                output_dir = Path("outputs/zed_live_samples")
                output_dir.mkdir(exist_ok=True)
                
                cv2.imwrite(str(output_dir / f"left_rgb_{timestamp}.png"), left_bgr)
                cv2.imwrite(str(output_dir / f"right_rgb_{timestamp}.png"), right_bgr)
                cv2.imwrite(str(output_dir / f"depth_colored_{timestamp}.png"), depth_colored)
                cv2.imwrite(str(output_dir / f"pointcloud_top_{timestamp}.png"), pc_top_view)
                
                # Save raw depth as numpy array
                np.save(output_dir / f"depth_raw_{timestamp}.npy", depth_map)
                np.save(output_dir / f"pointcloud_raw_{timestamp}.npy", pointcloud)
                
                print(f"📸 Saved sample frames to {output_dir}")
        
        # Final statistics
        final_time = time.time() - start_time
        final_fps = frame_count / final_time
        print(f"📊 Final statistics:")
        print(f"   - Total frames: {frame_count}")
        print(f"   - Total time: {final_time:.1f}s")
        print(f"   - Average FPS: {final_fps:.1f}")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error during capture: {e}")
    finally:
        # Clean up
        cv2.destroyAllWindows()
        if 'camera' in locals():
            camera.disconnect()
        print("✅ Live capture stopped")

if __name__ == "__main__":
    live_multimodal_capture()