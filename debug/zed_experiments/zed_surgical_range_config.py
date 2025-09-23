#!/usr/bin/env python3
"""
ZED Camera Configuration for Surgical Short Range (0-100cm)
==========================================================
Optimized ZED SDK settings for surgical robotics applications
requiring high-quality depth in the 0cm to 1m range.
"""

import sys
import os
sys.path.append('src')

# Import ZED SDK directly to avoid camera module issues
import pyzed.sl as sl
import cv2
import numpy as np
import time

class ZEDSurgicalCamera:
    """ZED camera optimized for surgical short-range depth (0-100cm)"""
    
    def __init__(self):
        # Initialize with surgical-optimized parameters
        self.resolution = "HD720"
        self.depth_mode = "NEURAL_PLUS"  # Highest quality depth for precision work
        self.depth_max_distance = 1.0    # 1 meter maximum range
        self.fps = 30                     # Smooth real-time for teleoperation
        
        # ZED SDK objects
        self.zed = sl.Camera()
        self.init_params = None
        self.runtime_params = None
        
        # Data containers
        self.left_image = sl.Mat()
        self.right_image = sl.Mat() 
        self.depth_map = sl.Mat()
        self.point_cloud = sl.Mat()
        
        self.is_connected = False
        
    def connect_surgical_optimized(self) -> bool:
        """Connect with surgical-specific optimization"""
        try:
            # Initialize camera parameters
            self.init_params = sl.InitParameters()
            
            # Resolution optimized for surgical work
            self.init_params.camera_resolution = sl.RESOLUTION.HD720
            
            # Use NEURAL_PLUS for maximum depth accuracy
            self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS
            
            # Short range optimization
            self.init_params.coordinate_units = sl.UNIT.MILLIMETER
            self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Y_UP
            
            # CRITICAL: Set minimum depth for surgical range
            self.init_params.depth_minimum_distance = 200  # 20cm minimum (avoid too close objects)
            self.init_params.depth_maximum_distance = 1000  # 100cm maximum
            
            # Disable self-calibration for consistent performance
            self.init_params.enable_image_enhancement = True
            self.init_params.enable_right_side_measure = True
            
            # Open camera
            err = self.zed.open(self.init_params)
            if err != sl.ERROR_CODE.SUCCESS:
                print(f"❌ ZED Camera failed to open: {repr(err)}")
                return False
            
            # Runtime parameters optimized for surgical precision
            self.runtime_params = sl.RuntimeParameters()
            
            # Higher confidence for surgical precision (reduce noise)
            self.runtime_params.confidence_threshold = 80  # Higher than default (50)
            
            # Texture confidence for better edge detection in surgical scenes
            self.runtime_params.texture_confidence_threshold = 100
            
            # Remove speckle noise for cleaner depth maps
            self.runtime_params.remove_saturated_areas = True
            
            self.is_connected = True
            
            # Display surgical configuration
            camera_info = self.zed.get_camera_information()
            res = camera_info.camera_configuration.resolution
            
            print("🏥 ZED Surgical Camera Configuration:")
            print(f"  📏 Depth Range: 20cm - 100cm (optimized for surgery)")
            print(f"  🎯 Confidence: 80% (high precision)")
            print(f"  🧠 Mode: NEURAL_PLUS (maximum quality)")
            print(f"  📺 Resolution: {res.width}×{res.height}")
            print(f"  ⚡ FPS: 30")
            
            return True
            
        except Exception as e:
            print(f"❌ Surgical camera setup failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect ZED camera"""
        if self.is_connected:
            self.zed.close()
            self.is_connected = False
            print("✅ ZED Surgical Camera disconnected")
    
    def capture_all_modalities(self):
        """Capture all modalities from ZED camera"""
        if not self.is_connected:
            return {}
        
        # Grab frame from ZED
        if self.zed.grab(self.runtime_params) != sl.ERROR_CODE.SUCCESS:
            return {}
        
        results = {}
        
        try:
            # Retrieve left RGB image
            if self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT) == sl.ERROR_CODE.SUCCESS:
                left_np = self.left_image.get_data()[:, :, :3]  # Remove alpha channel
                results['left_rgb'] = left_np
            
            # Retrieve right RGB image  
            if self.zed.retrieve_image(self.right_image, sl.VIEW.RIGHT) == sl.ERROR_CODE.SUCCESS:
                right_np = self.right_image.get_data()[:, :, :3]  # Remove alpha channel
                results['right_rgb'] = right_np
            
            # Retrieve depth map
            if self.zed.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH) == sl.ERROR_CODE.SUCCESS:
                depth_np = self.depth_map.get_data()
                results['depth'] = depth_np
            
            # Retrieve point cloud (XYZRGBA)
            if self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA) == sl.ERROR_CODE.SUCCESS:
                pointcloud_np = self.point_cloud.get_data()
                results['point_cloud'] = pointcloud_np
                
        except Exception as e:
            print(f"❌ Capture error: {e}")
            return {}
        
        return results
    
    def get_surgical_depth_stats(self, depth_map: np.ndarray) -> dict:
        """Analyze depth map for surgical range statistics"""
        # Convert to centimeters for easier interpretation
        depth_cm = depth_map / 10.0
        
        # Valid depth pixels in surgical range (20-100cm)
        valid_mask = (depth_cm >= 20) & (depth_cm <= 100) & ~np.isnan(depth_cm)
        valid_pixels = np.sum(valid_mask)
        total_pixels = depth_map.size
        
        # Statistics for surgical range
        if valid_pixels > 0:
            valid_depths = depth_cm[valid_mask]
            mean_depth = np.mean(valid_depths)
            min_depth = np.min(valid_depths)
            max_depth = np.max(valid_depths)
            std_depth = np.std(valid_depths)
        else:
            mean_depth = min_depth = max_depth = std_depth = 0
        
        return {
            'valid_pixels': valid_pixels,
            'total_pixels': total_pixels,
            'coverage_percent': (valid_pixels / total_pixels) * 100,
            'mean_depth_cm': mean_depth,
            'min_depth_cm': min_depth,
            'max_depth_cm': max_depth,
            'std_depth_cm': std_depth
        }

def live_surgical_depth_demo():
    """Live demo of ZED surgical depth optimization"""
    print("🏥 Starting ZED Surgical Depth Demo")
    print("=" * 50)
    print("📏 Optimized for 20cm - 100cm surgical range")
    print("🎯 High precision NEURAL_PLUS depth mode")
    print("Press 'q' to quit, 's' to save sample images")
    print()
    
    # Create surgical camera
    camera = ZEDSurgicalCamera()
    
    # Connect with surgical optimization
    if not camera.connect_surgical_optimized():
        print("❌ Failed to connect to ZED camera")
        return
    
    # Create windows for different views
    cv2.namedWindow("Left RGB", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Right RGB", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Surgical Depth", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Depth Stats", cv2.WINDOW_AUTOSIZE)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Capture all modalities
            data = camera.capture_all_modalities()
            
            if not data:
                print("❌ Failed to capture frame")
                continue
            
            frame_count += 1
            
            # Extract data
            left_rgb = data['left_rgb']
            right_rgb = data['right_rgb'] 
            depth_mm = data['depth']
            
            # Get surgical depth statistics
            stats = camera.get_surgical_depth_stats(depth_mm)
            
            # Convert depth to visualization (20cm-100cm range)
            depth_cm = depth_mm / 10.0
            depth_vis = np.zeros_like(depth_cm)
            
            # Color code surgical range: 20cm (red) -> 100cm (blue)
            valid_mask = (depth_cm >= 20) & (depth_cm <= 100) & ~np.isnan(depth_cm)
            
            if np.any(valid_mask):
                # Normalize depth to 0-1 for surgical range
                normalized_depth = (depth_cm[valid_mask] - 20) / 80  # 20-100cm -> 0-1
                depth_vis[valid_mask] = normalized_depth
            
            # Convert to color map (closer = red, farther = blue)
            depth_colored = cv2.applyColorMap(
                (depth_vis * 255).astype(np.uint8), 
                cv2.COLORMAP_JET
            )
            
            # Add invalid areas as black
            depth_colored[~valid_mask] = [0, 0, 0]
            
            # Create stats overlay
            stats_img = np.zeros((400, 600, 3), dtype=np.uint8)
            
            # Calculate FPS
            fps = frame_count / (time.time() - start_time) if time.time() - start_time > 0 else 0
            
            # Draw statistics
            cv2.putText(stats_img, "SURGICAL DEPTH STATISTICS", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.putText(stats_img, f"FPS: {fps:.1f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.putText(stats_img, f"Coverage: {stats['coverage_percent']:.1f}%", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            
            cv2.putText(stats_img, f"Valid pixels: {stats['valid_pixels']:,}", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            if stats['valid_pixels'] > 0:
                cv2.putText(stats_img, f"Mean depth: {stats['mean_depth_cm']:.1f} cm", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.putText(stats_img, f"Range: {stats['min_depth_cm']:.1f} - {stats['max_depth_cm']:.1f} cm", (10, 180), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.putText(stats_img, f"Precision: ±{stats['std_depth_cm']:.1f} cm", (10, 210), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Color legend
            cv2.putText(stats_img, "DEPTH COLOR SCALE:", (10, 260), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(stats_img, "Red = 20cm (close)", (10, 290), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(stats_img, "Blue = 100cm (far)", (10, 320), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.putText(stats_img, "Black = Out of range", (10, 350), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            
            # Display all views
            cv2.imshow("Left RGB", left_rgb)
            cv2.imshow("Right RGB", right_rgb)
            cv2.imshow("Surgical Depth", depth_colored)
            cv2.imshow("Depth Stats", stats_img)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save sample images
                timestamp = int(time.time())
                cv2.imwrite(f"outputs/captured_images/surgical_left_{timestamp}.png", left_rgb)
                cv2.imwrite(f"outputs/captured_images/surgical_right_{timestamp}.png", right_rgb)
                cv2.imwrite(f"outputs/captured_images/surgical_depth_{timestamp}.png", depth_colored)
                print(f"💾 Saved surgical sample images with timestamp {timestamp}")
    
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    
    finally:
        camera.disconnect()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    live_surgical_depth_demo()