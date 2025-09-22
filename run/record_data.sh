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
DEFAULT_TASK="Dissect chicken thigh"
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
    echo "  -r, --resume           Resume existing dataset (add more episodes)"
    echo "  --delete               Delete existing dataset and start fresh"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use defaults"
    echo "  $0 -n 10 -t 'Pick and place cube'    # Custom episodes and task"
    echo "  $0 -d my-dataset -n 3                # Custom dataset name"
    echo "  $0 -r -n 3                           # Resume existing + 3 more episodes"
    echo "  $0 --delete                          # Delete existing and start fresh"
    echo ""
    echo -e "${BOLD}${BLUE}⌨️  Keyboard Controls During Recording:${NC}"
    echo -e "${CYAN}  →  Right Arrow:${NC}  Early stop current episode/reset → move to next"
    echo -e "${CYAN}  ←  Left Arrow: ${NC}  Cancel current episode → re-record it"
    echo -e "${CYAN}  ⎋  Escape:     ${NC}  Stop session → encode videos → upload dataset"
    echo ""
    echo -e "${BOLD}${BLUE}📊 Recording Features:${NC}"
    echo -e "${CYAN}  • Data Storage:${NC}     LeRobotDataset format, auto-uploaded to Hugging Face"
    echo -e "${CYAN}  • Checkpointing:${NC}    Automatic checkpoints, resume with --resume=true"
    echo -e "${CYAN}  • Episode Time:${NC}     60 seconds per episode (default)"
    echo -e "${CYAN}  • Reset Time:${NC}       60 seconds between episodes (default)"
}

# Parse command line arguments
NUM_EPISODES=$DEFAULT_NUM_EPISODES
TASK_DESCRIPTION="$DEFAULT_TASK"
DATASET_NAME="$DEFAULT_DATASET_NAME"
RESUME_RECORDING=false
DELETE_EXISTING=false

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
        -r|--resume)
            RESUME_RECORDING=true
            shift
            ;;
        --delete)
            DELETE_EXISTING=true
            shift
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

# Handle existing dataset
DATASET_PATH="/home/maxboels/.cache/huggingface/lerobot/${HF_USER}/${DATASET_NAME}"

if [ -d "$DATASET_PATH" ]; then
    echo -e "${YELLOW}⚠️  Existing dataset found: ${DATASET_NAME}${NC}"
    
    if [ "$DELETE_EXISTING" = true ]; then
        echo -e "${YELLOW}🗑️  Deleting existing dataset...${NC}"
        rm -rf "$DATASET_PATH"
        echo -e "${GREEN}✅ Dataset deleted. Starting fresh.${NC}"
        echo ""
    elif [ "$RESUME_RECORDING" = true ]; then
        echo -e "${CYAN}🔄 Resuming existing dataset (adding $NUM_EPISODES more episodes)${NC}"
        echo ""
    else
        echo ""
        echo "Options:"
        echo "1. Resume existing dataset (add more episodes): ./lesurgeon.sh record -r -n $NUM_EPISODES"
        echo "2. Delete existing and start fresh:            ./lesurgeon.sh record --delete"
        echo "3. Use a different dataset name:               ./lesurgeon.sh record -d new-dataset-name"
        echo ""
        echo -e "${RED}❌ Use one of the options above to proceed.${NC}"
        exit 1
    fi
fi

# Display recording configuration
echo -e "${CYAN}📊 Recording Configuration:${NC}"
echo "  - Episodes:    $NUM_EPISODES"
echo "  - Task:        $TASK_DESCRIPTION"
echo "  - Dataset:     ${HF_USER}/${DATASET_NAME}"
echo "  - Cameras:     /dev/video0 (wrist), /dev/video2 (external) @ 1280x720 30fps"
echo ""

# Display keyboard controls
echo -e "${BOLD}${BLUE}⌨️  Keyboard Controls During Recording:${NC}"
echo -e "${CYAN}  →  Right Arrow:${NC}  Early stop current episode/reset → move to next"
echo -e "${CYAN}  ←  Left Arrow: ${NC}  Cancel current episode → re-record it"
echo -e "${CYAN}  ⎋  Escape:     ${NC}  Stop session → encode videos → upload dataset"
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

# Build the recording command
RECORD_CMD="lerobot-record"
RECORD_CMD="$RECORD_CMD --robot.type=so101_follower"
RECORD_CMD="$RECORD_CMD --robot.port=\"$FOLLOWER_PORT\""
RECORD_CMD="$RECORD_CMD --robot.id=lesurgeon_follower_arm"
RECORD_CMD="$RECORD_CMD --robot.cameras=\"{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, external: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}}\""
RECORD_CMD="$RECORD_CMD --teleop.type=so101_leader"
RECORD_CMD="$RECORD_CMD --teleop.port=\"$LEADER_PORT\""
RECORD_CMD="$RECORD_CMD --teleop.id=lesurgeon_leader_arm"
RECORD_CMD="$RECORD_CMD --display_data=true"
RECORD_CMD="$RECORD_CMD --dataset.repo_id=\"${HF_USER}/${DATASET_NAME}\""
RECORD_CMD="$RECORD_CMD --dataset.num_episodes=\"$NUM_EPISODES\""
RECORD_CMD="$RECORD_CMD --dataset.single_task=\"$TASK_DESCRIPTION\""

# Add resume flag if resuming
if [ "$RESUME_RECORDING" = true ]; then
    RECORD_CMD="$RECORD_CMD --resume=true"
fi

# Run the recording command
printf "\n\n" | eval $RECORD_CMD

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