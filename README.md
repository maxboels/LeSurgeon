# LeSurgeon - LeRobot Development Environment

## 🤖 LeRobot Environment Setup

This project now includes a complete LeRobot development environment with Python 3.10 and all required dependencies.

### Quick Start

**Using the convenience script (recommended):**
```bash
./lesurgeon.sh activate    # Activate environment
./lesurgeon.sh status      # Check robot status  
./lesurgeon.sh calibrate   # Calibrate robots
./lesurgeon.sh teleoperate # Start teleoperation session
./lesurgeon.sh help        # Show all commands
```

**Manual commands:**
1. **Activate the environment:**
   ```bash
   source setup/activate_lerobot.sh
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

### What's Included

- **Python 3.10** virtual environment in `.lerobot/`
- **LeRobot** with all optional dependencies (`lerobot[all]`)
- **System dependencies:** ffmpeg, cmake, build tools, robotics libraries
- **Weights & Biases** integration for experiment tracking
- **Development tools:** pre-commit, pytest, debugging tools

### Project Structure

- **setup/** - Environment setup and configuration scripts
  - `activate_lerobot.sh` - Environment activation script
  - `setup_wandb.py` - Weights & Biases configuration
  - `setup_summary.sh` - Environment setup documentation
- **run/** - Operational scripts for robot tasks
  - `teleoperate.sh` - Start teleoperation session
  - `robot_status.sh` - Check robot calibration status
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

Once your robots are calibrated, you can:

**Teleoperation (Control follower with leader arm):**
```bash
./lesurgeon.sh teleoperate    # Easy way
# OR manually:
bash run/teleoperate.sh       # Direct command
```

**Data Recording:**
```bash
lerobot-record --robot=lesurgeon_follower_arm --teleop=lesurgeon_leader_arm
```

**Check Robot Status:**
```bash
./lesurgeon.sh status         # Check calibration and connection status
```

### STL Files

The `stl_files/` directory contains 3D models and G-code files for the robotics hardware.

### Documentation

- [LeRobot Documentation](https://lerobot.huggingface.co/)
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [Weights & Biases Docs](https://docs.wandb.ai/)

---

Happy robot learning! 🚀