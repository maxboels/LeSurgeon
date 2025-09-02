#!/bin/bash

# Create conda environment with Python 3.10
conda create -n lerobot python=3.10 -y

# Activate the conda environment
conda activate lerobot

# Install system dependencies
# sudo apt-get update
# sudo apt-get install -y cmake build-essential python-dev pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev

# Upgrade pip to latest version
pip install --upgrade pip

# Install lerobot package
pip install lerobot

echo "Conda environment 'lerobot' created successfully!"
echo "To activate it, run: conda activate lerobot"
echo "To deactivate it, run: conda deactivate"


# Motor Control
pip install -e ".[feetech]" # or "[dynamixel]" for example


# Weight and Biases
wandb login
