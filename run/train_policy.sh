#!/bin/bash
# Policy Training Script
# =====================
# Trains ML policies using LeRobot on recorded datasets

# Source environment variables
source "$(dirname "$0")/../.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_POLICY_TYPE="act"
DEFAULT_DEVICE="cuda"

show_usage() {
    echo -e "${BLUE}🧠 Policy Training${NC}"
    echo "=================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --dataset NAME     Dataset name (default: from .env)"
    echo "  -p, --policy TYPE      Policy type (default: $DEFAULT_POLICY_TYPE)"
    echo "  -v, --device DEVICE    Training device (default: $DEFAULT_DEVICE)"
    echo "  -r, --resume           Resume from checkpoint"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Train with defaults"
    echo "  $0 -d my-dataset -p act              # Train ACT policy"
    echo "  $0 -r                                 # Resume training"
}

# Parse command line arguments
DATASET_NAME="${DEFAULT_DATASET_NAME:-lesurgeon-recordings}"
POLICY_TYPE="$DEFAULT_POLICY_TYPE"
DEVICE="$DEFAULT_DEVICE"
RESUME=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dataset)
            DATASET_NAME="$2"
            shift 2
            ;;
        -p|--policy)
            POLICY_TYPE="$2"
            shift 2
            ;;
        -v|--device)
            DEVICE="$2"
            shift 2
            ;;
        -r|--resume)
            RESUME=true
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

echo -e "${BLUE}🧠 Policy Training${NC}"
echo "=================="
echo ""

# Check if authenticated
if [ -z "$HF_USER" ]; then
    echo -e "${YELLOW}⚠️  Hugging Face user not set. Running authentication...${NC}"
    bash "$(dirname "$0")/../setup/setup_huggingface.sh"
    source "$(dirname "$0")/../.env"
fi

# Set up training configuration
POLICY_NAME="${DEFAULT_POLICY_NAME:-lesurgeon-policy}"
JOB_NAME="${POLICY_TYPE}_${DATASET_NAME}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

echo -e "${CYAN}🎯 Training Configuration:${NC}"
echo "  - Dataset:    ${HF_USER}/${DATASET_NAME}"
echo "  - Policy:     $POLICY_TYPE"
echo "  - Device:     $DEVICE"
echo "  - Job Name:   $JOB_NAME"
echo "  - Output:     $OUTPUT_DIR"
echo "  - Resume:     $RESUME"
echo ""

# Activate environment
source .lerobot/bin/activate

if [ "$RESUME" = true ]; then
    # Resume training from checkpoint
    CHECKPOINT_CONFIG="$OUTPUT_DIR/checkpoints/last/pretrained_model/train_config.json"
    
    if [ ! -f "$CHECKPOINT_CONFIG" ]; then
        echo -e "${RED}❌ Checkpoint config not found: $CHECKPOINT_CONFIG${NC}"
        echo "Available training outputs:"
        ls -la outputs/train/ 2>/dev/null || echo "No training outputs found"
        exit 1
    fi
    
    echo -e "${YELLOW}🔄 Resuming training from checkpoint...${NC}"
    echo ""
    
    lerobot-train \
        --config_path="$CHECKPOINT_CONFIG" \
        --resume=true
        
else
    # Start new training
    echo -e "${YELLOW}🚀 Starting new training...${NC}"
    echo ""
    
    lerobot-train \
        --dataset.repo_id="${HF_USER}/${DATASET_NAME}" \
        --policy.type="$POLICY_TYPE" \
        --output_dir="$OUTPUT_DIR" \
        --job_name="$JOB_NAME" \
        --policy.device="$DEVICE" \
        --wandb.enable=true \
        --policy.repo_id="${HF_USER}/${POLICY_NAME}"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Training completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Training Information:${NC}"
    echo "  - Output directory: $OUTPUT_DIR"
    echo "  - Policy repository: https://huggingface.co/${HF_USER}/${POLICY_NAME}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  - Resume training: ./run/train_policy.sh -r"
    echo "  - Run inference:   ./run/run_inference.sh -d ${DATASET_NAME}"
    echo "  - Replay episodes: ./run/replay_episodes.sh -d ${DATASET_NAME}"
else
    echo ""
    echo -e "${RED}❌ Training failed. Please check the error messages above.${NC}"
    exit 1
fi