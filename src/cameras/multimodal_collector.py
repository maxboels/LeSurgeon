#!/usr/bin/env python3
"""
Multi-Modal Camera Data Collector for LeRobot
==============================================
Collects rich multi-modal camera data including RGB, depth, and 3D points
for advanced surgical robot training.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import cv2
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from src.cameras.zed_multimodal_camera import ZEDMultiModalCamera

class MultiModalCollector:
    """
    Multi-modal camera data collector that saves RGB + depth + 3D data
    """
    
    def __init__(self, 
                 output_dir: str = "outputs/multimodal_training_data",
                 zed_resolution: str = "hd",
                 save_pointclouds: bool = True,
                 save_depth_maps: bool = True,
                 depth_max_distance: float = 800.0):
        """
        Initialize enhanced camera collector
        
        Args:
            output_dir: Directory to save enhanced data
            zed_resolution: ZED resolution mode ('hd', 'fhd', 'fast')
            save_pointclouds: Whether to save 3D point cloud data
            save_depth_maps: Whether to save depth map data
            depth_max_distance: Maximum depth for surgical workspace (mm)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.save_pointclouds = save_pointclouds
        self.save_depth_maps = save_depth_maps
        self.depth_max_distance = depth_max_distance
        
        # Initialize ZED multi-modal camera
        self.zed_camera = ZEDMultiModalCamera(
            **self._get_zed_config(zed_resolution),
            compute_depth=save_depth_maps,
            compute_pointcloud=save_pointclouds
        )
        
        # Episode tracking
        self.current_episode = 0
        self.current_frame = 0
        
        # Metadata tracking
        self.episode_metadata = {}
        
    def _get_zed_config(self, resolution: str) -> Dict[str, Any]:
        """Get ZED configuration for resolution"""
        configs = {
            'fast': {
                'width': 1344, 'height': 376, 'fps': 60,
                'depth_algorithm': 'BM', 'max_disparity': 64
            },
            'hd': {
                'width': 2560, 'height': 720, 'fps': 30,
                'depth_algorithm': 'SGBM', 'max_disparity': 96
            },
            'fhd': {
                'width': 3840, 'height': 1080, 'fps': 15,
                'depth_algorithm': 'SGBM', 'max_disparity': 128
            }
        }
        return configs.get(resolution, configs['hd'])
    
    def start_collection(self):
        """Start camera collection"""
        print("🌐 Starting Enhanced Camera Collection")
        print(f"📁 Output directory: {self.output_dir}")
        self.zed_camera.connect()
        
    def stop_collection(self):
        """Stop camera collection"""
        self.zed_camera.disconnect()
        self._save_collection_summary()
        
    def start_episode(self, episode_id: int, task_description: str):
        """Start new episode"""
        self.current_episode = episode_id
        self.current_frame = 0
        
        # Create episode directory
        episode_dir = self.output_dir / f"episode_{episode_id:04d}"
        episode_dir.mkdir(exist_ok=True)
        
        self.episode_metadata = {
            'episode_id': episode_id,
            'task_description': task_description,
            'start_time': time.time(),
            'frame_count': 0,
            'camera_mode': 'zed_multimodal',
            'depth_enabled': self.save_depth_maps,
            'pointcloud_enabled': self.save_pointclouds
        }
        
        print(f"🎬 Episode {episode_id} started: {task_description}")
    
    def capture_frame(self, action: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Capture enhanced frame with all modalities
        
        Args:
            action: Robot action vector for this frame
            
        Returns:
            Dictionary with all captured data
        """
        # Capture multi-modal data from ZED
        zed_data = self.zed_camera.capture_multi_modal()
        
        # Build comprehensive frame data
        frame_data = {
            'frame_id': self.current_frame,
            'episode_id': self.current_episode,
            'timestamp': time.time(),
            'action': action.tolist() if action is not None else None,
            
            # RGB data
            'rgb_left': zed_data['left_rgb'],
            'rgb_right': zed_data['right_rgb'],
            'rgb_stereo': zed_data['stereo_rgb'],
            
            # Processing metadata
            'processing_time': zed_data['metadata']['total_compute_time'],
            'camera_resolution': zed_data['metadata']['resolution'],
        }
        
        # Add depth data if available
        if self.save_depth_maps and 'depth' in zed_data:
            depth = np.clip(zed_data['depth'], 0, self.depth_max_distance)
            frame_data['depth'] = depth
            frame_data['depth_stats'] = {
                'valid_pixels': int(np.sum(depth > 0)),
                'mean_depth': float(np.mean(depth[depth > 0])) if np.any(depth > 0) else 0.0,
                'min_depth': float(np.min(depth[depth > 0])) if np.any(depth > 0) else 0.0,
                'max_depth': float(np.max(depth[depth > 0])) if np.any(depth > 0) else 0.0,
            }
        
        # Add point cloud if available
        if self.save_pointclouds and 'point_cloud' in zed_data:
            pc = zed_data['point_cloud']
            # Filter to surgical workspace
            if len(pc) > 0:
                valid_z = (pc[:, 2] > 0) & (pc[:, 2] < self.depth_max_distance)
                pc_filtered = pc[valid_z]
                frame_data['pointcloud'] = pc_filtered
                frame_data['pointcloud_stats'] = {
                    'num_points': len(pc_filtered),
                    'workspace_coverage': float(len(pc_filtered) / max(len(pc), 1)),
                }
            else:
                frame_data['pointcloud'] = np.empty((0, 6), dtype=np.float32)
                frame_data['pointcloud_stats'] = {'num_points': 0, 'workspace_coverage': 0.0}
        
        # Save frame data
        self._save_frame(frame_data)
        
        self.current_frame += 1
        self.episode_metadata['frame_count'] = self.current_frame
        
        return frame_data
    
    def _save_frame(self, frame_data: Dict[str, Any]):
        """Save frame data to disk"""
        episode_dir = self.output_dir / f"episode_{self.current_episode:04d}"
        frame_id = frame_data['frame_id']
        
        # Save RGB images
        cv2.imwrite(
            str(episode_dir / f"rgb_left_{frame_id:06d}.png"),
            cv2.cvtColor(frame_data['rgb_left'], cv2.COLOR_RGB2BGR)
        )
        cv2.imwrite(
            str(episode_dir / f"rgb_right_{frame_id:06d}.png"), 
            cv2.cvtColor(frame_data['rgb_right'], cv2.COLOR_RGB2BGR)
        )
        
        # Save depth data
        if 'depth' in frame_data:
            # Save raw depth as numpy array
            np.save(episode_dir / f"depth_{frame_id:06d}.npy", frame_data['depth'])
            
            # Save depth visualization
            depth_norm = cv2.normalize(frame_data['depth'], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_colored = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
            cv2.imwrite(str(episode_dir / f"depth_viz_{frame_id:06d}.png"), depth_colored)
        
        # Save point cloud
        if 'pointcloud' in frame_data:
            np.save(episode_dir / f"pointcloud_{frame_id:06d}.npy", frame_data['pointcloud'])
        
        # Save frame metadata
        metadata = {k: v for k, v in frame_data.items() 
                   if k not in ['rgb_left', 'rgb_right', 'rgb_stereo', 'depth', 'pointcloud']}
        
        with open(episode_dir / f"metadata_{frame_id:06d}.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def end_episode(self):
        """End current episode and save metadata"""
        if self.current_episode >= 0:
            self.episode_metadata['end_time'] = time.time()
            self.episode_metadata['duration'] = (
                self.episode_metadata['end_time'] - self.episode_metadata['start_time']
            )
            
            episode_dir = self.output_dir / f"episode_{self.current_episode:04d}"
            with open(episode_dir / "episode_metadata.json", 'w') as f:
                json.dump(self.episode_metadata, f, indent=2)
                
            print(f"✅ Episode {self.current_episode} completed: {self.current_frame} frames")
    
    def _save_collection_summary(self):
        """Save overall collection summary"""
        summary = {
            'collection_end_time': time.time(),
            'total_episodes': self.current_episode + 1 if self.current_episode >= 0 else 0,
            'camera_configuration': {
                'zed_multimodal': True,
                'depth_enabled': self.save_depth_maps,
                'pointcloud_enabled': self.save_pointclouds,
                'depth_max_distance_mm': self.depth_max_distance,
            },
            'output_directory': str(self.output_dir),
        }
        
        with open(self.output_dir / "collection_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"📊 Collection summary saved to {self.output_dir}/collection_summary.json")

def demonstrate_enhanced_collection():
    """Demonstrate enhanced camera data collection"""
    print("🎥 Enhanced Camera Collection Demo")
    print("=" * 50)
    
    # Create collector
    collector = MultiModalCollector(
        output_dir="outputs/demo_multimodal_data",
        zed_resolution="hd",
        save_pointclouds=True,
        save_depth_maps=True,
        depth_max_distance=600.0  # 60cm surgical workspace
    )
    
    try:
        # Start collection
        collector.start_collection()
        
        # Simulate an episode
        collector.start_episode(0, "Needle grasping and passing with depth sensing")
        
        print("🎬 Capturing enhanced frames...")
        for i in range(5):
            # Simulate robot action (6-DOF)
            fake_action = np.random.randn(6) * 0.1
            
            frame_data = collector.capture_frame(action=fake_action)
            
            print(f"  Frame {i+1}:")
            print(f"    Processing time: {frame_data['processing_time']:.3f}s")
            if 'depth_stats' in frame_data:
                stats = frame_data['depth_stats']
                print(f"    Depth: {stats['valid_pixels']:,} pixels, {stats['mean_depth']:.1f}mm mean")
            if 'pointcloud_stats' in frame_data:
                stats = frame_data['pointcloud_stats']
                print(f"    Point cloud: {stats['num_points']:,} points")
        
        # End episode
        collector.end_episode()
        
        # Stop collection
        collector.stop_collection()
        
        print(f"\n🎉 Enhanced collection demo completed!")
        print(f"📁 Check outputs/demo_enhanced_data/ for rich multi-modal data")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        collector.stop_collection()

if __name__ == "__main__":
    demonstrate_enhanced_collection()