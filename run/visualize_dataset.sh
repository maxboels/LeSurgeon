#!/bin/bash
# Dataset Visualization Script
# ===========================
# Visualize recorded datasets using LeRobot tools

# Source environment variables
source "$(dirname "$0")/../.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_usage() {
    echo -e "${BLUE}📊 Dataset Visualization${NC}"
    echo "======================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --dataset NAME     Dataset name (default: from .env)"
    echo "  -e, --episode NUM      Specific episode to visualize (optional)"
    echo "  -o, --output DIR       Output directory for visualizations"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Visualize default dataset"
    echo "  $0 -e 3                # Visualize episode 3"
    echo "  $0 -d my-data -o viz   # Custom dataset and output"
}

# Parse command line arguments
DATASET_NAME="${DEFAULT_DATASET_NAME:-lesurgeon-recordings}"
EPISODE=""
OUTPUT_DIR="outputs/visualizations"

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
        -o|--output)
            OUTPUT_DIR="$2"
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

echo -e "${BLUE}📊 Dataset Visualization${NC}"
echo "======================="
echo ""

# Check if authenticated
if [ -z "$HF_USER" ]; then
    echo -e "${YELLOW}⚠️  Hugging Face user not set. Running authentication...${NC}"
    bash "$(dirname "$0")/../setup/setup_huggingface.sh"
    source "$(dirname "$0")/../.env"
fi

echo -e "${CYAN}📈 Visualization Configuration:${NC}"
echo "  - Dataset: ${HF_USER}/${DATASET_NAME}"
if [ -n "$EPISODE" ]; then
    echo "  - Episode: $EPISODE"
else
    echo "  - Episodes: All"
fi
echo "  - Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}🚀 Starting dataset visualization...${NC}"
echo ""

# Activate environment
source .lerobot/bin/activate

# Run LeRobot visualization
if [ -n "$EPISODE" ]; then
    echo -e "${YELLOW}📊 Visualizing episode $EPISODE...${NC}"
    lerobot-visualize \
        --repo-id "${HF_USER}/${DATASET_NAME}" \
        --episode-id "$EPISODE" \
        --output-dir "$OUTPUT_DIR"
else
    echo -e "${YELLOW}📊 Visualizing all episodes...${NC}"
    lerobot-visualize \
        --repo-id "${HF_USER}/${DATASET_NAME}" \
        --output-dir "$OUTPUT_DIR"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Visualization completed!${NC}"
    echo ""
    echo -e "${BLUE}📁 Output Files:${NC}"
    ls -la "$OUTPUT_DIR"
    echo ""
    echo -e "${CYAN}View your visualizations:${NC}"
    echo "  - Open files in: $OUTPUT_DIR"
    echo "  - Dataset URL: https://huggingface.co/datasets/${HF_USER}/${DATASET_NAME}"
else
    echo ""
    echo -e "${RED}❌ Visualization failed. Please check the error messages above.${NC}"
    exit 1
fi