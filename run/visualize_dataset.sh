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
    echo "  -d, --dataset NAME     Dataset name (required)"
    echo "  -e, --episode NUM      Specific episode to visualize (optional)"
    echo "  -o, --output DIR       Output directory for visualizations"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -d my-dataset      # Visualize specific dataset"
    echo "  $0 -d my-data -e 3    # Visualize episode 3 of specific dataset"
    echo "  $0 -d my-data -o viz  # Custom dataset and output"
}

# Parse command line arguments
DATASET_NAME="${DEFAULT_DATASET_NAME:-}"
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

# Check if dataset name is provided
if [ -z "$DATASET_NAME" ]; then
    echo -e "${RED}❌ Dataset name is required. Use -d/--dataset to specify a dataset name.${NC}"
    show_usage
    exit 1
fi

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

# Open LeRobot visualization web app
VISUALIZATION_URL="https://huggingface.co/spaces/lerobot/visualize_dataset"

echo -e "${YELLOW}🌐 Opening LeRobot Dataset Visualization web app...${NC}"
echo ""
echo -e "${CYAN}📊 Visualization Information:${NC}"
echo "  - Web App:     $VISUALIZATION_URL"
echo "  - Your Dataset: ${HF_USER}/${DATASET_NAME}"
if [ -n "$EPISODE" ]; then
    echo "  - Episode:     $EPISODE"
else
    echo "  - Episodes:    All available"
fi
echo ""

# Try to open the URL in the default browser
if command -v xdg-open > /dev/null; then
    echo -e "${GREEN}� Opening visualization web app in your browser...${NC}"
    xdg-open "$VISUALIZATION_URL" &
elif command -v open > /dev/null; then
    echo -e "${GREEN}🚀 Opening visualization web app in your browser...${NC}"
    open "$VISUALIZATION_URL" &
else
    echo -e "${YELLOW}⚠️  Could not automatically open browser.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Visualization setup completed!${NC}"
echo ""
echo -e "${BLUE}� Instructions:${NC}"
echo "  1. Visit: $VISUALIZATION_URL"
echo "  2. Enter your dataset: ${HF_USER}/${DATASET_NAME}"
if [ -n "$EPISODE" ]; then
    echo "  3. Select episode: $EPISODE"
else
    echo "  3. Browse all episodes interactively"
fi
echo ""
echo -e "${CYAN}Additional Resources:${NC}"
echo "  - Dataset URL: https://huggingface.co/datasets/${HF_USER}/${DATASET_NAME}"
echo "  - LeRobot Docs: https://lerobot.huggingface.co/"