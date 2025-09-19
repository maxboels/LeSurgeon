# LeSurgeon - LeRobot Development Environment

## 🤖 LeRobot Environment Setup

This project now includes a complete LeRobot development environment with Python 3.10 and all required dependencies.

### Quick Start

1. **Activate the environment:**
   ```bash
   source activate_lerobot.sh
   ```

2. **Test the installation:**
   ```bash
   python -c "import lerobot; print('LeRobot works!')"
   ```

3. **Setup Weights & Biases (if needed):**
   ```bash
   python setup_wandb.py
   ```

### What's Included

- **Python 3.10** virtual environment in `.lerobot/`
- **LeRobot** with all optional dependencies (`lerobot[all]`)
- **System dependencies:** ffmpeg, cmake, build tools, robotics libraries
- **Weights & Biases** integration for experiment tracking
- **Development tools:** pre-commit, pytest, debugging tools

### Environment Files

- `.lerobot/` - Python virtual environment (ignored by git)
- `activate_lerobot.sh` - Convenient activation script
- `setup_wandb.py` - Weights & Biases configuration helper
- `setup_summary.sh` - Environment setup summary
- `.gitignore` - Comprehensive ignore rules for ML/robotics projects

### STL Files

The `stl_files/` directory contains 3D models and G-code files for the robotics hardware.

### Documentation

- [LeRobot Documentation](https://lerobot.huggingface.co/)
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [Weights & Biases Docs](https://docs.wandb.ai/)

---

Happy robot learning! 🚀