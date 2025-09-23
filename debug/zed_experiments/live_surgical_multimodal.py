#!/usr/bin/env python3
"""
Live ZED Ultra-Short Range Multi-Modal Display
==============================================
Real-time display of all ZED SDK modalities optimized for 10cm-45cm surgical range.
Shows: Left RGB, Right RGB, Depth, Point Cloud, Confidence, and Normals.
"""

import sys
import pyzed.sl as sl
import cv2
import numpy as np
import time

class ZEDSurgicalLiveDisplay:
    """Live display system for ZED surgical modalities"""
    
    def __init__(self):
        self.camera = None
        
    def setup_surgical_camera(self):
        """Setup ZED camera for ultra-short surgical range"""
        self.camera = sl.Camera()
        
        # Ultra-short range surgical configuration
        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720
        init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS
        init_params.coordinate_units = sl.UNIT.MILLIMETER
        init_params.depth_minimum_distance = 150  # 15cm (will be clamped if too close)
        init_params.depth_maximum_distance = 450  # 45cm
        init_params.enable_image_enhancement = True
        init_params.enable_right_side_measure = True
        init_params.depth_stabilization = 50
        
        err = self.camera.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print(f"❌ Camera failed to open: {err}")
            return False
        
        # Runtime parameters for surgical precision
        self.runtime_params = sl.RuntimeParameters()
        self.runtime_params.confidence_threshold = 90
        self.runtime_params.texture_confidence_threshold = 100
        self.runtime_params.remove_saturated_areas = True
        
        # Data containers
        self.left_image = sl.Mat()
        self.right_image = sl.Mat()
        self.depth_map = sl.Mat()
        self.confidence_map = sl.Mat()
        self.point_cloud = sl.Mat()
        
        print("✅ ZED camera configured for ultra-short surgical range")
        return True
    
    def create_depth_visualization(self, depth_data):
        """Create color-coded depth visualization for 15-45cm range"""
        depth_cm = depth_data / 10.0  # Convert mm to cm
        
        # Focus on surgical range (15-45cm)
        depth_vis = np.zeros_like(depth_cm, dtype=np.uint8)
        
        # Create mask for valid surgical range
        valid_mask = (depth_cm >= 15) & (depth_cm <= 45) & ~np.isnan(depth_cm)
        
        if np.any(valid_mask):
            # Normalize depth to 0-255 for surgical range (15cm=0, 45cm=255)
            normalized = ((depth_cm[valid_mask] - 15) / 30) * 255
            depth_vis[valid_mask] = normalized.astype(np.uint8)
        
        # Apply color map (closer=red, farther=blue)
        depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)
        
        # Set invalid areas to black
        depth_colored[~valid_mask] = [0, 0, 0]
        
        return depth_colored
    
    def create_confidence_visualization(self, confidence_data):
        """Visualize confidence map (0=high confidence, 100=low confidence)"""
        # Invert confidence so high confidence = bright
        confidence_vis = (100 - confidence_data).astype(np.uint8)
        return cv2.applyColorMap(confidence_vis, cv2.COLORMAP_PLASMA)
    
    def add_surgical_overlay(self, image, depth_data):
        """Add surgical information overlay"""
        # Calculate surgical metrics
        depth_cm = depth_data / 10.0
        surgical_mask = (depth_cm >= 15) & (depth_cm <= 45) & ~np.isnan(depth_cm)
        surgical_pixels = np.sum(surgical_mask)
        total_pixels = depth_data.size
        coverage = (surgical_pixels / total_pixels) * 100
        
        if surgical_pixels > 0:
            surgical_depths = depth_cm[surgical_mask]
            mean_depth = np.mean(surgical_depths)
            min_depth = np.min(surgical_depths)
            max_depth = np.max(surgical_depths)
        else:
            mean_depth = min_depth = max_depth = 0
        
        # Create overlay
        overlay = image.copy()
        h, w = overlay.shape[:2]
        
        # Semi-transparent background for text
        cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # Add surgical metrics text
        cv2.putText(image, "SURGICAL DEPTH METRICS", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        cv2.putText(image, f"Range: 15-45cm (Ultra-Short)", (20, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(image, f"Coverage: {coverage:.1f}%", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.putText(image, f"Mean: {mean_depth:.1f}cm", (20, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(image, f"Range: {min_depth:.1f}-{max_depth:.1f}cm", (20, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(image, f"Mode: NEURAL_PLUS (Max Quality)", (20, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return image
    
    def run_live_display(self):
        """Run live multi-modal surgical display"""
        if not self.setup_surgical_camera():
            return
        
        print("\n🔬 ZED Ultra-Short Range Live Display")
        print("=" * 50)
        print("📏 Surgical Range: 15cm - 45cm")
        print("🎯 NEURAL_PLUS + 90% confidence")
        print("Press 'q' to quit, 's' to save frame")
        print("Press 'r' to reset view")
        
        # Create windows
        cv2.namedWindow("Left RGB + Metrics", cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("Right RGB", cv2.WINDOW_AUTOSIZE)  
        cv2.namedWindow("Surgical Depth (15-45cm)", cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("Confidence Map", cv2.WINDOW_AUTOSIZE)
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                if self.camera.grab(self.runtime_params) == sl.ERROR_CODE.SUCCESS:
                    # Retrieve all data
                    self.camera.retrieve_image(self.left_image, sl.VIEW.LEFT)
                    self.camera.retrieve_image(self.right_image, sl.VIEW.RIGHT)
                    self.camera.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH)
                    self.camera.retrieve_measure(self.confidence_map, sl.MEASURE.CONFIDENCE)
                    
                    # Convert to numpy arrays
                    left_rgb = self.left_image.get_data()[:, :, :3]
                    right_rgb = self.right_image.get_data()[:, :, :3]
                    depth_data = self.depth_map.get_data()
                    confidence_data = self.confidence_map.get_data()
                    
                    # Create visualizations
                    depth_colored = self.create_depth_visualization(depth_data)
                    confidence_colored = self.create_confidence_visualization(confidence_data)
                    
                    # Add surgical overlay to left image
                    left_with_metrics = self.add_surgical_overlay(left_rgb.copy(), depth_data)
                    
                    # Display all views
                    cv2.imshow("Left RGB + Metrics", left_with_metrics)
                    cv2.imshow("Right RGB", right_rgb)
                    cv2.imshow("Surgical Depth (15-45cm)", depth_colored)
                    cv2.imshow("Confidence Map", confidence_colored)
                    
                    frame_count += 1
                    
                    # Calculate and display FPS every 30 frames
                    if frame_count % 30 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed if elapsed > 0 else 0
                        print(f"FPS: {fps:.1f} | Frames: {frame_count}")
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    timestamp = int(time.time())
                    cv2.imwrite(f"outputs/captured_images/surgical_live_left_{timestamp}.png", left_with_metrics)
                    cv2.imwrite(f"outputs/captured_images/surgical_live_depth_{timestamp}.png", depth_colored)
                    print(f"💾 Saved surgical live frames with timestamp {timestamp}")
                elif key == ord('r'):
                    # Reset statistics
                    frame_count = 0
                    start_time = time.time()
                    print("🔄 Display statistics reset")
        
        except KeyboardInterrupt:
            print("\n⏹️  Live display stopped by user")
        
        finally:
            self.camera.close()
            cv2.destroyAllWindows()
            print("✅ ZED camera disconnected")

if __name__ == "__main__":
    display = ZEDSurgicalLiveDisplay()
    display.run_live_display()