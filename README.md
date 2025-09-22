# LeSurgeon - LeRobot Development Environment

## 🤖 LeRobot Environment Setup

This project includes a complete LeRobot development environment with Python 3.10 and all required dependencies.

### Environment Activation

**For active development (recommended):**
```bash
source setup/activate_lerobot.sh
```
This activates the environment in your current shell - you'll see `(.lerobot)` in your prompt.

**For information display:**
```bash
./lesurgeon.sh activate
```
This shows environment information but returns you to your original shell when finished.

### Quick Start

**Environment Activation:**
```bash
# Method 1: Direct activation (recommended for development)
source setup/activate_lerobot.sh     # Keeps you in activated environment with (.lerobot) prompt

# Method 2: Information display only
./lesurgeon.sh activate              # Shows environment info but returns to original shell
```

**Robot Operations:**
```bash
./lesurgeon.sh identify      # Identify which arm is leader/follower (setup)
./lesurgeon.sh status        # Check robot status  
./lesurgeon.sh calibrate     # Calibrate robots
./lesurgeon.sh teleoperate   # Standard teleoperation
./lesurgeon.sh teleop-cam    # Camera-enabled teleoperation (U20CAM-1080p)
```

**Data & Machine Learning:**
```bash
./lesurgeon.sh hf-setup      # Setup Hugging Face authentication
./lesurgeon.sh record        # Record teleoperation data for ML
./lesurgeon.sh train         # Train ML policy on data
./lesurgeon.sh inference     # Run trained policy
./lesurgeon.sh help          # Show all commands
```

**Manual commands:**
1. **Activate the environment (for development work):**
   ```bash
   source setup/activate_lerobot.sh
   # You'll see (.lerobot) in your prompt indicating the environment is active
   ```

2. **Test the installation:**
   ```bash
   python -c "import lerobot; print('LeRobot works!')"
   ```

3. **Setup Weights & Biases (if needed):**
   ```bash
   python setup/setup_wandb.py
   ```

4. **Start teleoperation:**
   ```bash
   bash run/teleoperate.sh
   ```

> **Note:** The difference between `./lesurgeon.sh activate` and `source setup/activate_lerobot.sh`:
> - `./lesurgeon.sh activate` displays environment information but doesn't keep you in the activated environment
> - `source setup/activate_lerobot.sh` actually activates the environment in your current shell (recommended for development)

### What's Included

- **Python 3.10** virtual environment in `.lerobot/`
- **LeRobot** with all optional dependencies (`lerobot[all]`)
- **System dependencies:** ffmpeg, cmake, build tools, robotics libraries
- **Weights & Biases** integration for experiment tracking
- **Development tools:** pre-commit, pytest, debugging tools

### Project Structure

- **setup/** - Environment setup and configuration scripts
  - `activate_lerobot.sh` - Environment activation script
  - `setup_huggingface.sh` - Hugging Face authentication and setup
  - `identify_arms_interactive.sh` - Interactive arm identification wizard
  - `verify_arm_identification.sh` - Verify current arm mappings
  - `setup_wandb.py` - Weights & Biases configuration
  - `setup_summary.sh` - Environment setup documentation
- **run/** - Operational scripts for robot tasks
  - `teleoperate.sh` - Standard teleoperation session
  - `teleoperate_with_camera.sh` - Camera-enabled teleoperation (U20CAM-1080p @ 720p)
  - `robot_status.sh` - Check robot calibration status
  - `record_data.sh` - Record teleoperation data for ML training
  - `upload_dataset.sh` - Upload datasets to Hugging Face Hub
  - `train_policy.sh` - Train ML policies on recorded data
  - `run_inference.sh` - Run trained policy inference
  - `replay_episodes.sh` - Replay recorded episodes
  - `visualize_dataset.sh` - Visualize datasets
- **config/** - Robot configuration and calibration data
  - `calibration.sh` - Robot calibration commands
  - `calibration_backups/` - Backup copies of calibration files
- **debug/** - Diagnostic and troubleshooting tools
  - `diagnose_motors.py` - Motor diagnostic script
  - `simple_motor_check.py` - Simple motor position checker
- **docs/** - Documentation and guides
- **stl_files/** - 3D models and G-code files
- **.lerobot/** - Python virtual environment (ignored by git)

### Robot Operations

**First-time setup - Identify your arms:**
```bash
./lesurgeon.sh identify      # Interactive wizard to identify leader/follower arms
```

Once your robots are calibrated, you can:

**Teleoperation (Control follower with leader arm):**
```bash
./lesurgeon.sh teleoperate    # Standard teleoperation (no camera)
./lesurgeon.sh teleop-cam     # Camera-enabled teleoperation with U20CAM-1080p
# OR manually:
bash run/teleoperate.sh       # Direct standard command
bash run/teleoperate_with_camera.sh  # Direct camera command
```

**Data Recording:**
```bash
./lesurgeon.sh record        # Interactive data recording with camera
./lesurgeon.sh record -n 10 -t "Pick and place cube"  # Custom episodes and task
```

**Check Robot Status:**
```bash
./lesurgeon.sh status         # Check calibration and connection status
```

### Machine Learning Workflow

**Setup (first time only):**
```bash
./lesurgeon.sh hf-setup      # Authenticate with Hugging Face
```

**Complete ML Pipeline:**
```bash
# 1. Record training data
./lesurgeon.sh record -n 10 -t "Surgical task demonstration"

# 2. Upload dataset to Hugging Face
./lesurgeon.sh upload

# 3. Train a policy
./lesurgeon.sh train -p act

# 4. Run inference with trained policy
./lesurgeon.sh inference

# 5. Replay episodes for verification
./lesurgeon.sh replay -e 0

# 6. Visualize your data
./lesurgeon.sh visualize
```

**Advanced ML Commands:**
```bash
# Resume training from checkpoint
./lesurgeon.sh train -r

# Train with custom dataset and policy type
./lesurgeon.sh train -d my-dataset -p act -v cuda

# Run inference with teleop fallback
./lesurgeon.sh inference --teleop

# Replay specific episodes
./lesurgeon.sh replay -e 3 -d my-dataset

# Visualize specific episodes
./lesurgeon.sh visualize -e 5 -o my_viz_folder
```

### STL Files

The `stl_files/` directory contains 3D models and G-code files for the robotics hardware.

### Arm Identification

**Why identify arms?**
The system needs to distinguish between the leader arm (controller) and follower arm (mimic). The identification wizard prevents confusion by letting you physically connect each arm when prompted.

**First-time setup:**
```bash
./lesurgeon.sh identify      # Run the interactive identification wizard
```

**Verify current setup:**
```bash
./setup/verify_arm_identification.sh    # Check current arm mappings
```

The identification process:
1. Disconnect both arms
2. Connect only the LEADER arm (the one you control) when prompted
3. Connect the FOLLOWER arm (the one that mimics) when prompted
4. Configuration is automatically saved and tested

**Manual identification scripts:**
```bash
./setup/identify_arms_interactive.sh    # Direct script access
./setup/verify_arm_identification.sh    # Direct verification
```

### Documentation

- [LeRobot Documentation](https://lerobot.huggingface.co/)
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [Weights & Biases Docs](https://docs.wandb.ai/)

---

Happy robot learning! 🚀