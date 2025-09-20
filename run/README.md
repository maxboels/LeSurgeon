# Run Scripts Directory

This directory contains all operational scripts for the LeSurgeon robot system, from basic teleoperation to complete machine learning workflows.

## 📁 Directory Structure

```
run/
├── README.md                    # This file
├── record_data.sh              # Record teleoperation data for ML training
├── replay_episodes.sh          # Replay recorded episodes on the robot
├── robot_status.sh             # Check robot calibration and connection status
├── run_inference.sh            # Run trained ML policy inference
├── teleoperate_auto.sh         # Auto-confirm teleoperation
├── teleoperate.sh              # Standard teleoperation
├── teleoperate_with_camera.sh  # Camera-enabled teleoperation
├── train_policy.sh             # Train ML policies on recorded data
├── upload_dataset.sh           # Upload datasets to Hugging Face Hub
└── visualize_dataset.sh        # Generate dataset visualizations
```

## 🎮 Robot Operation Scripts

### Basic Teleoperation

**`teleoperate.sh`** - Standard teleoperation
- Automatically detects ARM ports
- Auto-confirms calibration
- Basic leader-follower control

**`teleoperate_with_camera.sh`** - Camera-enabled teleoperation
- Includes U20CAM-1080p camera support (1280x720 @ 30fps)
- Automatic port detection
- Auto-confirms calibration for both arms
- Real-time visual feedback

**`teleoperate_auto.sh`** - Auto-confirm teleoperation
- Same as standard but with additional auto-confirmation
- Useful for automated workflows

**`robot_status.sh`** - System diagnostics
- Check robot calibration status
- Verify ARM connections
- Display system information

## 🎥 Data Collection Scripts

### Recording Data

**`record_data.sh`** - Interactive data recording
```bash
./record_data.sh                              # Use defaults
./record_data.sh -n 10 -t "Pick and place"   # Custom episodes and task
./record_data.sh -d my-dataset -n 5           # Custom dataset name
```

**Options:**
- `-n, --episodes NUM`: Number of episodes to record (default: 5)
- `-t, --task DESCRIPTION`: Task description (default: "Surgical robot teleoperation")
- `-d, --dataset NAME`: Dataset name (default: "lesurgeon-recordings")

**Features:**
- Automatic ARM port detection
- Camera integration (wrist camera)
- Hugging Face authentication check
- Real-time recording with visual feedback

### Data Management

**`upload_dataset.sh`** - Upload to Hugging Face Hub
```bash
./upload_dataset.sh                    # Upload default dataset
./upload_dataset.sh -d my-dataset      # Upload specific dataset
```

**`visualize_dataset.sh`** - Generate visualizations
```bash
./visualize_dataset.sh                 # Visualize all episodes
./visualize_dataset.sh -e 3            # Visualize episode 3
./visualize_dataset.sh -o viz_folder   # Custom output directory
```

## 🧠 Machine Learning Scripts

### Training

**`train_policy.sh`** - Train ML policies
```bash
./train_policy.sh                              # Train with defaults
./train_policy.sh -d my-dataset -p act         # Custom dataset and policy
./train_policy.sh -r                           # Resume from checkpoint
./train_policy.sh -v cpu                       # Use CPU instead of GPU
```

**Options:**
- `-d, --dataset NAME`: Dataset name
- `-p, --policy TYPE`: Policy type (default: "act")
- `-v, --device DEVICE`: Training device (default: "cuda")
- `-r, --resume`: Resume from checkpoint

**Supported Policy Types:**
- `act` - Action Chunking with Transformers
- `diffusion_policy` - Diffusion Policy
- `tdmpc` - Temporal Difference Model Predictive Control

### Inference & Evaluation

**`run_inference.sh`** - Run trained policy
```bash
./run_inference.sh                             # Use default policy
./run_inference.sh -p my-policy -t "New task"  # Custom policy and task
./run_inference.sh --teleop                    # Enable teleop fallback
```

**Options:**
- `-p, --policy NAME`: Policy name
- `-t, --task DESCRIPTION`: Task description
- `--teleop`: Enable teleoperation fallback

**`replay_episodes.sh`** - Replay recorded episodes
```bash
./replay_episodes.sh                    # Replay episode 0 from default dataset
./replay_episodes.sh -e 5               # Replay episode 5
./replay_episodes.sh -d my-data -e 2    # Custom dataset and episode
```

## 🚀 Quick Start Workflows

### 1. Basic Teleoperation
```bash
./teleoperate_with_camera.sh            # Start camera-enabled teleoperation
```

### 2. Data Collection Workflow
```bash
./record_data.sh -n 10 -t "Demo task"   # Record 10 episodes
./upload_dataset.sh                     # Upload to Hugging Face
./visualize_dataset.sh                  # Generate visualizations
```

### 3. ML Training Workflow
```bash
./train_policy.sh -d my-dataset         # Train policy
./run_inference.sh -p my-policy         # Test inference
./replay_episodes.sh -e 0               # Replay for verification
```

### 4. System Check
```bash
./robot_status.sh                       # Verify system status
```

## ⚙️ Prerequisites

Before using these scripts, ensure:

1. **Environment activated**: `source ../setup/activate_lerobot.sh`
2. **Arms identified**: `../lesurgeon.sh identify`
3. **Robots calibrated**: `../lesurgeon.sh calibrate`
4. **Hugging Face setup** (for ML workflows): `../setup/setup_huggingface.sh`

## 🔧 Technical Details

### Automatic Features
- **Port Detection**: All scripts use dynamic ARM port detection
- **Environment Management**: Automatic LeRobot environment activation
- **Calibration Handling**: Auto-confirmation of existing calibrations
- **Error Handling**: Comprehensive error checking and user guidance

### Camera Configuration
- **Device**: `/dev/video0` (U20CAM-1080p)
- **Resolution**: 1280x720 @ 30fps
- **Format**: MJPG (for stability)
- **Mount**: Wrist-mounted on follower arm

### ARM Configuration
- **Leader ARM**: Controller (the arm you manipulate)
- **Follower ARM**: Mimic (the arm that performs tasks)
- **Port Detection**: Based on hardware serial numbers
- **Calibration**: Automatic confirmation of existing calibration files

## 🐛 Troubleshooting

### Common Issues

**"ARM detection failed"**
- Check USB connections
- Run `../lesurgeon.sh identify` to re-identify arms
- Verify both arms are powered on

**"Calibration mismatch"**
- Scripts auto-confirm calibration
- If issues persist, recalibrate: `../lesurgeon.sh calibrate`

**"Hugging Face authentication failed"**
- Run `../setup/setup_huggingface.sh`
- Check `.env` file contains valid `HUGGINGFACE_TOKEN`

**"Camera not found"**
- Check `/dev/video0` exists
- Verify camera is connected to USB hub
- Try unplugging/reconnecting camera

### Debug Commands

```bash
# Check ARM detection
../debug/detect_arm_ports.sh

# Verify ARM identification
../setup/verify_arm_identification.sh

# Check robot status
./robot_status.sh

# Test camera
ls /dev/video*
```

## 📚 Related Documentation

- [Main README](../README.md) - Project overview and setup
- [Setup Documentation](../setup/) - Environment and authentication setup
- [Debug Tools](../debug/) - Diagnostic and troubleshooting tools
- [LeRobot Documentation](https://lerobot.huggingface.co/) - Official LeRobot docs

---

**Need help?** Check the main project [README](../README.md) or run `../lesurgeon.sh help` for available commands.