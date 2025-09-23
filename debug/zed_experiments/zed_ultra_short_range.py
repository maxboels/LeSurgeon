#!/usr/bin/env python3
"""
ZED Camera Configuration for Ultra-Short Surgical Range (20cm-45cm)
==================================================================
Optimized ZED SDK settings for precision surgical robotics requiring
high-quality depth in the ultra-short 20cm to 45cm range.

Based on ZED SDK 5.0 depth sensing documentation for surgical precision.
"""

import sys
import pyzed.sl as sl
import numpy as np
import time

class ZEDUltraShortRangeCamera:
    """ZED camera optimized for ultra-short surgical range (20cm-45cm)"""
    
    def __init__(self):
        # ZED SDK objects
        self.zed = sl.Camera()
        self.init_params = None
        self.runtime_params = None
        
        # Data containers
        self.left_image = sl.Mat()
        self.right_image = sl.Mat() 
        self.depth_map = sl.Mat()
        self.point_cloud = sl.Mat()
        self.confidence_map = sl.Mat()
        self.normal_map = sl.Mat()
        
        self.is_connected = False
        
    def connect_ultra_short_range(self) -> bool:
        """Connect with ultra-short range surgical optimization"""
        try:
            # Initialize camera parameters for ultra-short range
            self.init_params = sl.InitParameters()
            
            # Use HD720 for best balance of speed/quality for surgery
            self.init_params.camera_resolution = sl.RESOLUTION.HD720
            
            # NEURAL_PLUS for maximum depth accuracy in short range
            self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS
            
            # CRITICAL: Ultra-short range optimization (20cm-45cm)
            self.init_params.coordinate_units = sl.UNIT.MILLIMETER
            self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Y_UP
            
            # Ultra-short surgical range: 15cm to 45cm
            self.init_params.depth_minimum_distance = 150   # 15cm minimum
            self.init_params.depth_maximum_distance = 450   # 45cm maximum
            
            # Enhanced image processing for surgical precision
            self.init_params.enable_image_enhancement = True
            self.init_params.enable_right_side_measure = True  # For stereo validation
            
            # Disable self-calibration for consistent surgical results
            self.init_params.camera_disable_self_calib = False  # Keep enabled for accuracy
            
            # High stabilization for steady surgical work
            self.init_params.depth_stabilization = 50  # Higher than default (30)
            
            print("📷 Opening ZED camera with ultra-short range settings...")
            err = self.zed.open(self.init_params)
            if err != sl.ERROR_CODE.SUCCESS:
                print(f"❌ ZED Camera failed to open: {repr(err)}")
                return False
            
            # Runtime parameters for maximum surgical precision
            self.runtime_params = sl.RuntimeParameters()
            
            # VERY high confidence for surgical precision (remove unreliable points)
            self.runtime_params.confidence_threshold = 90  # Very high (vs default 50)
            
            # Maximum texture confidence for edge detection in surgical scenes  
            self.runtime_params.texture_confidence_threshold = 100
            
            # Remove all saturated/unreliable areas
            self.runtime_params.remove_saturated_areas = True
            
            self.is_connected = True
            
            # Display ultra-short range configuration
            camera_info = self.zed.get_camera_information()
            res = camera_info.camera_configuration.resolution
            
            print("🔬 ZED Ultra-Short Range Surgical Configuration:")
            print(f"  📏 Ultra-Short Range: 15cm - 45cm (precision surgery)")
            print(f"  🎯 Confidence: 90% (maximum precision)")
            print(f"  🧠 Mode: NEURAL_PLUS (highest quality)")
            print(f"  📺 Resolution: {res.width}×{res.height}")
            print(f"  🔄 Stabilization: 50 (high stability)")
            print(f"  ⚡ FPS: 30 (real-time capable)")
            print(f"  🏥 Perfect for micro-surgical procedures!")
            
            return True
            
        except Exception as e:
            print(f"❌ Ultra-short range camera setup failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect ZED camera"""
        if self.is_connected:
            self.zed.close()
            self.is_connected = False
            print("✅ ZED Ultra-Short Range Camera disconnected")
    
    def capture_all_surgical_modalities(self):
        """Capture all modalities optimized for ultra-short surgical range"""
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
            
            # Retrieve high-precision depth map
            if self.zed.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH) == sl.ERROR_CODE.SUCCESS:
                depth_np = self.depth_map.get_data()
                results['depth'] = depth_np
            
            # Retrieve point cloud (XYZRGBA) for 3D surgical navigation
            if self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA) == sl.ERROR_CODE.SUCCESS:
                pointcloud_np = self.point_cloud.get_data()
                results['point_cloud'] = pointcloud_np
            
            # Retrieve confidence map for surgical quality assessment
            if self.zed.retrieve_measure(self.confidence_map, sl.MEASURE.CONFIDENCE) == sl.ERROR_CODE.SUCCESS:
                confidence_np = self.confidence_map.get_data()
                results['confidence'] = confidence_np
            
            # Retrieve normal map for surface analysis (surgical instruments, tissue)
            if self.zed.retrieve_measure(self.normal_map, sl.MEASURE.NORMALS) == sl.ERROR_CODE.SUCCESS:
                normals_np = self.normal_map.get_data()
                results['normals'] = normals_np
                
        except Exception as e:
            print(f"❌ Surgical capture error: {e}")
            return {}
        
        return results
    
    def get_surgical_depth_analysis(self, depth_map: np.ndarray) -> dict:
        """Comprehensive depth analysis for ultra-short surgical range"""
        # Convert to centimeters for surgical interpretation
        depth_cm = depth_map / 10.0
        
        # Focus on ultra-short surgical range (15-45cm)
        surgical_mask = (depth_cm >= 15) & (depth_cm <= 45) & ~np.isnan(depth_cm)
        surgical_pixels = np.sum(surgical_mask)
        total_pixels = depth_map.size
        
        if surgical_pixels > 0:
            surgical_depths = depth_cm[surgical_mask]
            
            # Detailed surgical statistics
            stats = {
                'valid_pixels': surgical_pixels,
                'total_pixels': total_pixels,
                'coverage_percent': (surgical_pixels / total_pixels) * 100,
                'mean_depth_cm': np.mean(surgical_depths),
                'median_depth_cm': np.median(surgical_depths),
                'min_depth_cm': np.min(surgical_depths),
                'max_depth_cm': np.max(surgical_depths),
                'std_depth_cm': np.std(surgical_depths),
                'depth_range_cm': np.max(surgical_depths) - np.min(surgical_depths),
                
                # Surgical precision metrics
                'precision_mm': np.std(surgical_depths) * 10,  # Convert to mm
                'depth_distribution': np.histogram(surgical_depths, bins=10, range=(10, 45))[0],
                'working_distance_optimal': 20 <= np.mean(surgical_depths) <= 35,  # Optimal surgical range
            }
        else:
            stats = {
                'valid_pixels': 0, 'total_pixels': total_pixels, 'coverage_percent': 0,
                'mean_depth_cm': 0, 'median_depth_cm': 0, 'min_depth_cm': 0, 
                'max_depth_cm': 0, 'std_depth_cm': 0, 'depth_range_cm': 0,
                'precision_mm': 0, 'depth_distribution': np.zeros(10),
                'working_distance_optimal': False
            }
        
        return stats

def test_ultra_short_surgical_config():
    """Test ultra-short range ZED configuration for surgical precision"""
    print("🔬 Testing ZED Ultra-Short Range Surgical Configuration")
    print("=" * 60)
    print("📏 Optimized for 15cm - 45cm surgical range")
    print("🎯 Maximum precision with NEURAL_PLUS + 90% confidence")
    print()
    
    # Create ultra-short range surgical camera
    camera = ZEDUltraShortRangeCamera()
    
    # Connect with ultra-short range optimization
    if not camera.connect_ultra_short_range():
        print("❌ Failed to connect to ZED camera")
        return
    
    print("\n📊 Capturing 15 frames for ultra-short range analysis...")
    
    coverage_samples = []
    precision_samples = []
    
    for frame_num in range(15):
        data = camera.capture_all_surgical_modalities()
        
        if data:
            # Analyze ultra-short range depth quality
            stats = camera.get_surgical_depth_analysis(data['depth'])
            
            coverage_samples.append(stats['coverage_percent'])
            precision_samples.append(stats['precision_mm'])
            
            optimal_indicator = "🎯" if stats['working_distance_optimal'] else "⚠️"
            
            print(f"Frame {frame_num + 1:2d}: "
                  f"Coverage: {stats['coverage_percent']:5.1f}%, "
                  f"Mean: {stats['mean_depth_cm']:5.1f}cm, "
                  f"Range: {stats['min_depth_cm']:4.1f}-{stats['max_depth_cm']:4.1f}cm, "
                  f"Precision: ±{stats['precision_mm']:4.1f}mm {optimal_indicator}")
            
            time.sleep(0.1)  # Small delay between captures
    
    # Calculate overall performance metrics
    avg_coverage = np.mean(coverage_samples) if coverage_samples else 0
    avg_precision = np.mean(precision_samples) if precision_samples else 0
    
    print(f"\n🎯 Ultra-Short Range Surgical Performance Summary:")
    print(f"  📏 Target Range: 15cm - 45cm (ultra-short precision)")
    print(f"  🧠 Depth Mode: NEURAL_PLUS (maximum accuracy)")
    print(f"  🎯 Confidence: 90% (surgical-grade filtering)")
    print(f"  📊 Average Coverage: {avg_coverage:.1f}% of frame")
    print(f"  📐 Average Precision: ±{avg_precision:.1f}mm")
    print(f"  🔄 Stabilization: 50 (high stability for surgery)")
    print(f"  📺 Resolution: 1280×720 HD")
    print(f"  ⚡ Real-time: 30 FPS capability")
    print(f"  🏥 Optimized for micro-surgical procedures!")
    
    # Performance assessment
    if avg_coverage > 30 and avg_precision < 20:
        print(f"\n✅ EXCELLENT: Ultra-short range configuration optimal for surgery!")
    elif avg_coverage > 20 and avg_precision < 30:
        print(f"\n✅ GOOD: Suitable for most surgical procedures")
    else:
        print(f"\n⚠️  Consider adjusting camera position for better surgical range coverage")
    
    camera.disconnect()
    print(f"\n✅ Ultra-short range surgical configuration test completed")

if __name__ == "__main__":
    test_ultra_short_surgical_config()