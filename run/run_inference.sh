#!/bin/bash
# Policy Inference Script
# =======================
# Run trained policy inference on the robot

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

show_usage() {
    echo -e "${BLUE}🤖 Policy Inference${NC}"
    echo "=================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -p, --policy NAME      Policy name (default: from .env)"
    echo "  -d, --dataset NAME     Evaluation dataset name (optional)"
    echo "  -t, --task DESCRIPTION Task description (default: from .env)"
    echo "  --teleop               Enable teleoperation fallback"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run inference with default policy"
    echo "  $0 -p my-policy -t 'Pick up cube'    # Custom policy and task"
    echo "  $0 --teleop                          # Enable teleop fallback"
}

# Parse command line arguments
POLICY_NAME="${DEFAULT_POLICY_NAME:-lesurgeon-policy}"
DATASET_NAME=""
TASK_DESCRIPTION="${DEFAULT_TASK_DESCRIPTION:-Surgical robot teleoperation}"
ENABLE_TELEOP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--policy)
            POLICY_NAME="$2"
            shift 2
            ;;
        -d|--dataset)
            DATASET_NAME="$2"
            shift 2
            ;;
        -t|--task)
            TASK_DESCRIPTION="$2"
            shift 2
            ;;
        --teleop)
            ENABLE_TELEOP=true
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

echo -e "${BLUE}🤖 Policy Inference${NC}"
echo "=================="
echo ""

# Check if authenticated
if [ -z "$HF_USER" ]; then
    echo -e "${YELLOW}⚠️  Hugging Face user not set. Running authentication...${NC}"
    bash "$(dirname "$0")/../setup/setup_huggingface.sh"
    source "$(dirname "$0")/../.env"
fi

# Detect ARM ports
echo -e "${YELLOW}🔍 Detecting ARM ports...${NC}"
if ! detect_arm_ports; then
    echo -e "${RED}❌ Failed to detect ARM ports. Please check connections.${NC}"
    exit 1
fi

if [ "$ENABLE_TELEOP" = true ]; then
    echo -e "${GREEN}✅ Arms detected:${NC}"
    echo "  - Leader:   $LEADER_PORT (for teleop fallback)"
    echo "  - Follower: $FOLLOWER_PORT"
else
    echo -e "${GREEN}✅ Follower arm found: $FOLLOWER_PORT${NC}"
fi
echo ""

# Set up evaluation dataset if provided
EVAL_DATASET=""
if [ -n "$DATASET_NAME" ]; then
    EVAL_DATASET="${HF_USER}/${DATASET_NAME}"
fi

echo -e "${CYAN}🎯 Inference Configuration:${NC}"
echo "  - Policy:     ${HF_USER}/${POLICY_NAME}"
echo "  - Task:       $TASK_DESCRIPTION"
echo "  - Robot:      $FOLLOWER_PORT"
echo "  - Camera:     /dev/video0 (1280x720 @ 30fps)"
echo "  - Teleop:     $ENABLE_TELEOP"
if [ -n "$EVAL_DATASET" ]; then
    echo "  - Eval Dataset: $EVAL_DATASET"
fi
echo ""

# Confirm inference
echo -e "${YELLOW}Start policy inference? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Inference cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Starting policy inference...${NC}"
echo ""

# Activate environment
source .lerobot/bin/activate

# Build the command
CMD="lerobot-record"
CMD="$CMD --robot.type=so101_follower"
CMD="$CMD --robot.port=$FOLLOWER_PORT"
CMD="$CMD --robot.id=lesurgeon_follower_arm"
CMD="$CMD --robot.cameras=\"{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}}\""
CMD="$CMD --display_data=false"

if [ -n "$EVAL_DATASET" ]; then
    CMD="$CMD --dataset.repo_id=$EVAL_DATASET"
else
    CMD="$CMD --dataset.repo_id=${HF_USER}/eval_${POLICY_NAME}"
fi

CMD="$CMD --dataset.single_task=\"$TASK_DESCRIPTION\""

if [ "$ENABLE_TELEOP" = true ]; then
    CMD="$CMD --teleop.type=so101_leader"
    CMD="$CMD --teleop.port=$LEADER_PORT"
    CMD="$CMD --teleop.id=lesurgeon_leader_arm"
fi

CMD="$CMD --policy.path=${HF_USER}/${POLICY_NAME}"

# Run the inference
printf "\n" | eval $CMD

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Policy inference completed!${NC}"
    if [ -n "$EVAL_DATASET" ]; then
        echo ""
        echo -e "${BLUE}📊 Evaluation Results:${NC}"
        echo "  - Dataset: $EVAL_DATASET"
    fi
else
    echo ""
    echo -e "${RED}❌ Inference failed. Please check the error messages above.${NC}"
    exit 1
fi