#!/bin/bash
# LeSurgeon Data Recording Script
# ==============================
# Records teleoperation data for training ML models

# Source environment variables and port detection
source "$(dirname "$0")/../.env"
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_NUM_EPISODES=5
DEFAULT_TASK="Surgical robot teleoperation"
DEFAULT_DATASET_NAME="lesurgeon-recordings"

show_usage() {
    echo -e "${BLUE}🎥 LeSurgeon Data Recording${NC}"
    echo "=========================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -n, --episodes NUM     Number of episodes to record (default: $DEFAULT_NUM_EPISODES)"
    echo "  -t, --task DESCRIPTION Task description (default: '$DEFAULT_TASK')"
    echo "  -d, --dataset NAME     Dataset name (default: '$DEFAULT_DATASET_NAME')"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use defaults"
    echo "  $0 -n 10 -t 'Pick and place cube'    # Custom episodes and task"
    echo "  $0 -d my-dataset -n 3                # Custom dataset name"
}

# Parse command line arguments
NUM_EPISODES=$DEFAULT_NUM_EPISODES
TASK_DESCRIPTION="$DEFAULT_TASK"
DATASET_NAME="$DEFAULT_DATASET_NAME"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--episodes)
            NUM_EPISODES="$2"
            shift 2
            ;;
        -t|--task)
            TASK_DESCRIPTION="$2"
            shift 2
            ;;
        -d|--dataset)
            DATASET_NAME="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🎥 LeSurgeon Data Recording${NC}"
echo "=========================="
echo ""

# Check environment setup
if [ -z "$HF_USER" ]; then
    echo -e "${YELLOW}⚠️  Hugging Face user not set. Running authentication setup...${NC}"
    bash "$(dirname "$0")/../setup/setup_huggingface.sh"
    source "$(dirname "$0")/../.env"
fi

# Detect ARM ports
echo -e "${YELLOW}🔍 Detecting ARM ports...${NC}"
if ! detect_arm_ports; then
    echo -e "${RED}❌ Failed to detect ARM ports. Please check connections.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Arms detected:${NC}"
echo "  - Leader:   $LEADER_PORT"
echo "  - Follower: $FOLLOWER_PORT"
echo ""

# Display recording configuration
echo -e "${CYAN}📊 Recording Configuration:${NC}"
echo "  - Episodes:    $NUM_EPISODES"
echo "  - Task:        $TASK_DESCRIPTION"
echo "  - Dataset:     ${HF_USER}/${DATASET_NAME}"
echo "  - Camera:      /dev/video0 (1280x720 @ 30fps)"
echo ""

# Confirm before recording
echo -e "${YELLOW}Ready to start recording? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Recording cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Starting data recording...${NC}"
echo ""

# Activate LeRobot environment
source .lerobot/bin/activate

# Run the recording command
printf "\n\n" | lerobot-record \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true \
    --dataset.repo_id="${HF_USER}/${DATASET_NAME}" \
    --dataset.num_episodes="$NUM_EPISODES" \
    --dataset.single_task="$TASK_DESCRIPTION"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Recording completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Dataset Information:${NC}"
    echo "  - Repository: https://huggingface.co/datasets/${HF_USER}/${DATASET_NAME}"
    echo "  - Episodes recorded: $NUM_EPISODES"
    echo "  - Task: $TASK_DESCRIPTION"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  - Upload dataset: ./run/upload_dataset.sh"
    echo "  - Train policy:   ./run/train_policy.sh"
    echo "  - Visualize data: ./run/visualize_dataset.sh"
else
    echo ""
    echo -e "${RED}❌ Recording failed. Please check the error messages above.${NC}"
    exit 1
fi