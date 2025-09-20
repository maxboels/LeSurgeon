#!/bin/bash
# Episode Replay Script
# =====================
# Replays recorded episodes on the robot

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
    echo -e "${BLUE}🔄 Episode Replay${NC}"
    echo "================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --dataset NAME     Dataset name (default: from .env)"
    echo "  -e, --episode NUM      Episode number to replay (default: 0)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Replay episode 0 from default dataset"
    echo "  $0 -e 5                # Replay episode 5"
    echo "  $0 -d my-data -e 2     # Replay episode 2 from specific dataset"
}

# Parse command line arguments
DATASET_NAME="${DEFAULT_DATASET_NAME:-lesurgeon-recordings}"
EPISODE=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dataset)
            DATASET_NAME="$2"
            shift 2
            ;;
        -e|--episode)
            EPISODE="$2"
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

echo -e "${BLUE}🔄 Episode Replay${NC}"
echo "================="
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

echo -e "${GREEN}✅ Follower arm found: $FOLLOWER_PORT${NC}"
echo ""

echo -e "${CYAN}🎬 Replay Configuration:${NC}"
echo "  - Dataset:  ${HF_USER}/${DATASET_NAME}"
echo "  - Episode:  $EPISODE"
echo "  - Robot:    $FOLLOWER_PORT"
echo ""

# Confirm replay
echo -e "${YELLOW}Start episode replay? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Replay cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Starting episode replay...${NC}"
echo ""

# Activate environment and run replay
source .lerobot/bin/activate

printf "\n" | lerobot-replay \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --dataset.repo_id="${HF_USER}/${DATASET_NAME}" \
    --dataset.episode="$EPISODE"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Episode replay completed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Replay failed. Please check the error messages above.${NC}"
    exit 1
fi