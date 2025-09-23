#!/usr/bin/env python3
"""
LeRobot ZED Multi-Modal Camera Interface
=======================================
LeRobot-compatible camera that provides RGB + depth + point cloud data
for enhanced surgical robotics training.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.cameras.zed_multimodal_camera import ZEDMultiModalCamera
import numpy as np
import torch
from typing import Dict, Any
import time

class LeRobotZEDCamera:
    """
    LeRobot-compatible ZED camera providing multi-modal data
    """
    
    def __init__(self, 
                 resolution: str = 'hd',  # 'hd', 'fhd', 'fast'
                 include_depth: bool = True,
                 include_pointcloud: bool = True,
                 depth_max_distance: float = 1000.0):  # mm
        """
        Initialize LeRobot ZED camera
        
        Args:
            resolution: 'hd' (1280x720), 'fhd' (1920x1080), 'fast' (672x376)
            include_depth: Include depth data in observations
            include_pointcloud: Include 3D point cloud data  
            depth_max_distance: Maximum depth in mm for surgical workspace
        """
        self.resolution = resolution
        self.include_depth = include_depth
        self.include_pointcloud = include_pointcloud
        self.depth_max_distance = depth_max_distance
        
        # Resolution configurations optimized for surgical tasks
        self.res_configs = {
            'fast': {
                'width': 1344, 'height': 376, 'fps': 60,
                'algorithm': 'BM', 'disparity': 64,
                'description': 'Fast real-time for quick movements'
            },
            'hd': {
                'width': 2560, 'height': 720, 'fps': 30,
                'algorithm': 'SGBM', 'disparity': 96,
                'description': 'High quality for precise manipulation'
            },
            'fhd': {
                'width': 3840, 'height': 1080, 'fps': 15, 
                'algorithm': 'SGBM', 'disparity': 128,
                'description': 'Ultra-high quality for detailed work'
            }
        }
        
        # Get configuration
        if resolution not in self.res_configs:
            raise ValueError(f"Resolution must be one of {list(self.res_configs.keys())}")
        
        config = self.res_configs[resolution]
        
        # Initialize ZED multi-modal camera
        self.zed_camera = ZEDMultiModalCamera(
            width=config['width'],
            height=config['height'],
            fps=config['fps'],
            depth_algorithm=config['algorithm'],
            max_disparity=config['disparity'],
            compute_depth=include_depth,
            compute_pointcloud=include_pointcloud
        )
        
        # Cache for processing stats
        self.stats = {
            'frames_captured': 0,
            'avg_processing_time': 0.0,
            'avg_depth_quality': 0.0,
            'avg_pointcloud_size': 0.0
        }
        
    def connect(self):
        """Connect to ZED camera"""
        self.zed_camera.connect()
        config = self.res_configs[self.resolution]
        print(f"🌐 LeRobot ZED Camera ready: {config['description']}")
        
    def disconnect(self):
        """Disconnect from camera"""
        self.zed_camera.disconnect()
        
    def read(self) -> Dict[str, Any]:
        """
        Read multi-modal observation for LeRobot
        
        Returns observations in format compatible with LeRobot:
        - 'rgb_left': Left eye RGB [H,W,3]
        - 'rgb_right': Right eye RGB [H,W,3] 
        - 'depth': Depth map [H,W] in mm (if enabled)
        - 'pointcloud': 3D points [N,6] X,Y,Z,R,G,B (if enabled)
        """
        data = self.zed_camera.capture_multi_modal()
        
        # Update stats
        self.stats['frames_captured'] += 1
        self.stats['avg_processing_time'] = (
            (self.stats['avg_processing_time'] * (self.stats['frames_captured'] - 1) + 
             data['metadata']['total_compute_time']) / self.stats['frames_captured']
        )
        
        # Build LeRobot observation
        observation = {
            'rgb_left': data['left_rgb'],
            'rgb_right': data['right_rgb'],
        }
        
        if self.include_depth and 'depth' in data:
            # Clip depth to surgical workspace
            depth = np.clip(data['depth'], 0, self.depth_max_distance)
            observation['depth'] = depth
            
            # Update depth quality stats
            valid_pixels = np.sum(depth > 0)
            total_pixels = depth.shape[0] * depth.shape[1]
            depth_quality = valid_pixels / total_pixels
            self.stats['avg_depth_quality'] = (
                (self.stats['avg_depth_quality'] * (self.stats['frames_captured'] - 1) + 
                 depth_quality) / self.stats['frames_captured']
            )
        
        if self.include_pointcloud and 'point_cloud' in data:
            pc = data['point_cloud']
            # Filter point cloud to surgical workspace
            if len(pc) > 0:
                valid_z = (pc[:, 2] > 0) & (pc[:, 2] < self.depth_max_distance)
                pc_filtered = pc[valid_z]
                observation['pointcloud'] = pc_filtered
                
                self.stats['avg_pointcloud_size'] = (
                    (self.stats['avg_pointcloud_size'] * (self.stats['frames_captured'] - 1) + 
                     len(pc_filtered)) / self.stats['frames_captured']
                )
            else:
                observation['pointcloud'] = np.empty((0, 6), dtype=np.float32)
        
        return observation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get camera performance statistics"""
        return self.stats.copy()

def test_lerobot_zed_integration():
    """Test LeRobot ZED integration"""
    print("🤖 Testing LeRobot ZED Integration")
    print("=" * 50)
    
    resolutions = ['fast', 'hd', 'fhd']
    
    for res in resolutions:
        print(f"\n🎯 Testing {res.upper()} resolution")
        print("-" * 30)
        
        try:
            # Create LeRobot ZED camera
            camera = LeRobotZEDCamera(
                resolution=res,
                include_depth=True,
                include_pointcloud=True,
                depth_max_distance=800.0  # 80cm max for surgery
            )
            
            camera.connect()
            
            # Capture multiple frames to test performance
            print("📊 Capturing test frames...")
            for i in range(5):
                obs = camera.read()
                
                print(f"  Frame {i+1}:")
                print(f"    RGB shapes: {obs['rgb_left'].shape}, {obs['rgb_right'].shape}")
                if 'depth' in obs:
                    depth_valid = np.sum(obs['depth'] > 0)
                    print(f"    Depth: {obs['depth'].shape}, {depth_valid:,} valid pixels")
                if 'pointcloud' in obs:
                    print(f"    Point cloud: {len(obs['pointcloud']):,} points")
            
            # Show performance stats
            stats = camera.get_stats()
            print(f"\n📈 Performance Summary:")
            print(f"    Avg processing time: {stats['avg_processing_time']:.3f}s")
            print(f"    Avg depth quality: {stats['avg_depth_quality']:.2%}")
            print(f"    Avg point cloud size: {stats['avg_pointcloud_size']:,.0f}")
            
            camera.disconnect()
            print(f"  ✅ {res.upper()} test completed")
            
        except Exception as e:
            print(f"  ❌ {res.upper()} test failed: {e}")
            continue

def demonstrate_surgical_capabilities():
    """Demonstrate surgical-specific capabilities"""
    print(f"\n🏥 Surgical Robotics Capabilities Demo")
    print("=" * 50)
    
    camera = LeRobotZEDCamera(
        resolution='hd',
        include_depth=True, 
        include_pointcloud=True,
        depth_max_distance=600.0  # 60cm surgical workspace
    )
    
    try:
        camera.connect()
        
        print("🎯 Capturing surgical workspace data...")
        obs = camera.read()
        
        # Analyze surgical-relevant metrics
        if 'depth' in obs:
            depth = obs['depth']
            
            # Find objects in typical needle/tool distance range
            needle_range = (50, 200)  # 5-20cm typical needle manipulation
            tool_range = (100, 400)   # 10-40cm tool workspace
            
            needle_pixels = np.sum((depth >= needle_range[0]) & (depth <= needle_range[1]))
            tool_pixels = np.sum((depth >= tool_range[0]) & (depth <= tool_range[1]))
            
            print(f"🪡 Needle manipulation range (5-20cm): {needle_pixels:,} pixels")
            print(f"🔧 Tool workspace range (10-40cm): {tool_pixels:,} pixels")
            
        if 'pointcloud' in obs:
            pc = obs['pointcloud']
            if len(pc) > 0:
                # Analyze 3D structure
                z_coords = pc[:, 2]
                closest_point = np.min(z_coords)
                furthest_point = np.max(z_coords)
                
                print(f"🌐 3D Point Cloud Analysis:")
                print(f"    Total points: {len(pc):,}")
                print(f"    Depth range: {closest_point:.1f}mm - {furthest_point:.1f}mm") 
                print(f"    Surgical workspace coverage: ✅")
        
        camera.disconnect()
        
        print(f"\n💡 Integration Benefits:")
        print(f"   • Rich spatial understanding from stereo + depth")
        print(f"   • 3D point clouds for object relationship modeling") 
        print(f"   • Multi-resolution support for different surgical phases")
        print(f"   • Optimized for real-time surgical robotics")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    test_lerobot_zed_integration()
    demonstrate_surgical_capabilities()