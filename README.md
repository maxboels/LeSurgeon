# LeSurgeon - LeRobot Development Environment

## 🤖 LeRobot Environment Setup

This project now includes a complete LeRobot development environment with Python 3.10 and all required dependencies.

### Quick Start

**Using the convenience script (recommended):**
```bash
./lesurgeon.sh activate    # Activate environment
./lesurgeon.sh status      # Check robot status  
./lesurgeon.sh calibrate   # Calibrate robots
./lesurgeon.sh help        # Show all commands
```

**Manual commands:**
1. **Activate the environment:**
   ```bash
   source scripts/activate_lerobot.sh
   ```

2. **Test the installation:**
   ```bash
   python -c "import lerobot; print('LeRobot works!')"
   ```

3. **Setup Weights & Biases (if needed):**
   ```bash
   python scripts/setup_wandb.py
   ```

### What's Included

- **Python 3.10** virtual environment in `.lerobot/`
- **LeRobot** with all optional dependencies (`lerobot[all]`)
- **System dependencies:** ffmpeg, cmake, build tools, robotics libraries
- **Weights & Biases** integration for experiment tracking
- **Development tools:** pre-commit, pytest, debugging tools

### Project Structure

- **scripts/** - Setup and utility scripts
  - `activate_lerobot.sh` - Environment activation script
  - `setup_wandb.py` - Weights & Biases configuration
  - `robot_status.sh` - Robot calibration status checker
  - `setup_summary.sh` - Environment setup documentation
- **config/** - Robot configuration and calibration data
  - `calibration.sh` - Robot calibration commands
  - `calibration_backups/` - Backup copies of calibration files
- **docs/** - Documentation and guides
- **stl_files/** - 3D models and G-code files
- **.lerobot/** - Python virtual environment (ignored by git)

### STL Files

The `stl_files/` directory contains 3D models and G-code files for the robotics hardware.

### Documentation

- [LeRobot Documentation](https://lerobot.huggingface.co/)
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [Weights & Biases Docs](https://docs.wandb.ai/)

---

Happy robot learning! 🚀