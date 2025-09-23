#!/bin/bash
# Policy Inference Script
# =======================
# Run trained policy inference on the robot

# Source environment variables and detection utilities
source "$(dirname "$0")/../.env"
source "$(dirname "$0")/../debug/detect_arm_ports.sh"
source "$(dirname "$0")/../src/utils/detect_cameras.sh"

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
    echo "  $0 --teleop                          # Enable teleop fallback for manual resets"
    echo "  $0 -p /path/to/model --teleop         # Local model with manual reset capability"
}

# Parse command line arguments
POLICY_NAME="${DEFAULT_POLICY_NAME:-lesurgeon-policy}"
DATASET_NAME=""
TASK_DESCRIPTION="${DEFAULT_TASK_DESCRIPTION:-Needle grasping and passing}"
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

# Detect camera configuration
echo -e "${YELLOW}📷 Detecting camera setup...${NC}"
if export_camera_config; then
    echo -e "${GREEN}✅ Camera setup: $CAMERA_DESCRIPTION${NC}"
else
    echo -e "${RED}❌ No compatible cameras detected. Please check connections.${NC}"
    exit 1
fi
echo ""

# Set up evaluation dataset if provided
EVAL_DATASET=""
if [ -n "$DATASET_NAME" ]; then
    EVAL_DATASET="${HF_USER}/${DATASET_NAME}"
fi

echo -e "${CYAN}🎯 Inference Configuration:${NC}"
if [[ "$POLICY_NAME" == /* ]]; then
    echo "  - Policy:     $POLICY_NAME"
else
    echo "  - Policy:     ${HF_USER}/${POLICY_NAME}"
fi
echo "  - Task:       $TASK_DESCRIPTION"
echo "  - Robot:      $FOLLOWER_PORT"
echo "  - Cameras:    $CAMERA_DESCRIPTION"
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
CMD="$CMD --robot.cameras=\"$CAMERA_CONFIG\""
CMD="$CMD --display_data=false"

if [ -n "$EVAL_DATASET" ]; then
    CMD="$CMD --dataset.repo_id=$EVAL_DATASET"
else
    # Generate evaluation dataset name based on policy type
    if [[ "$POLICY_NAME" == /* ]]; then
        # Local policy - use simple eval dataset name
        CMD="$CMD --dataset.repo_id=${HF_USER}/eval_local_policy"
    else
        # Remote policy - use policy name in dataset
        CMD="$CMD --dataset.repo_id=${HF_USER}/eval_${POLICY_NAME}"
    fi
fi

CMD="$CMD --dataset.single_task=\"$TASK_DESCRIPTION\""

if [ "$ENABLE_TELEOP" = true ]; then
    CMD="$CMD --teleop.type=so101_leader"
    CMD="$CMD --teleop.port=$LEADER_PORT"
    CMD="$CMD --teleop.id=lesurgeon_leader_arm"
fi

# Handle local vs remote policy paths
if [[ "$POLICY_NAME" == /* ]]; then
    # Absolute path - use as is (local checkpoint)
    CMD="$CMD --policy.path=$POLICY_NAME"
else
    # Relative path - assume it's a HuggingFace repo
    CMD="$CMD --policy.path=${HF_USER}/${POLICY_NAME}"
fi

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