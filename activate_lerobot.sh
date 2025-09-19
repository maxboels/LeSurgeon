#!/bin/bash
# LeRobot Environment Activation Script
# =====================================
# Convenient script to activate the lerobot environment and set up the development environment

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 Activating LeRobot Environment${NC}"
echo "=================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.lerobot"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found at $VENV_PATH${NC}"
    echo "Please run the setup script first to create the environment."
    exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

echo -e "${GREEN}✅ LeRobot environment activated!${NC}"
echo ""

# Display environment information
echo -e "${BLUE}📋 Environment Information:${NC}"
echo "Python version: $(python --version)"
echo "Python location: $(which python)"
echo "LeRobot version: $(python -c 'import lerobot; print(lerobot.__version__)' 2>/dev/null || echo 'Not available')"
echo "Wandb status: $(wandb --version 2>/dev/null || echo 'Not available')"
echo ""

# Display useful commands
echo -e "${YELLOW}🚀 Useful Commands:${NC}"
echo "• Test installation: python -c 'import lerobot; print(\"LeRobot imported successfully!\")'  "
echo "• Setup wandb: python setup_wandb.py"
echo "• List installed packages: pip list"
echo "• Deactivate environment: deactivate"
echo ""

echo -e "${YELLOW}📖 Documentation:${NC}"
echo "• LeRobot docs: https://lerobot.huggingface.co/"
echo "• Wandb docs: https://docs.wandb.ai/"
echo ""

# Set environment variables for better experience
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo -e "${GREEN}🎯 Ready to start your robotics journey!${NC}"
echo ""