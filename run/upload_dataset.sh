#!/bin/bash
# Dataset Upload Script
# ====================
# Uploads recorded dataset to Hugging Face Hub

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
    echo -e "${BLUE}📤 Dataset Upload to Hugging Face${NC}"
    echo "================================"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --dataset NAME     Dataset name (required)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -d my-dataset     # Upload specific dataset"
}

# Parse command line arguments
DATASET_NAME="${DEFAULT_DATASET_NAME:-}"

while [[ $# -gt 0 ]]; do
    case $1 in
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

echo -e "${BLUE}📤 Dataset Upload to Hugging Face${NC}"
echo "================================"
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

# Check if dataset directory exists
CACHE_DIR="$HOME/.cache/huggingface/lerobot"
DATASET_DIR="$CACHE_DIR/${HF_USER}--${DATASET_NAME}"

if [ ! -d "$DATASET_DIR" ]; then
    echo -e "${RED}❌ Dataset directory not found: $DATASET_DIR${NC}"
    echo ""
    echo "Available datasets:"
    ls -1 "$CACHE_DIR" 2>/dev/null | grep "^${HF_USER}--" | sed "s/^${HF_USER}--/  - /"
    exit 1
fi

echo -e "${CYAN}📊 Upload Configuration:${NC}"
echo "  - Dataset: ${HF_USER}/${DATASET_NAME}"
echo "  - Source:  $DATASET_DIR"
echo "  - Target:  https://huggingface.co/datasets/${HF_USER}/${DATASET_NAME}"
echo ""

# Confirm upload
echo -e "${YELLOW}Upload dataset to Hugging Face? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Upload cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Uploading dataset...${NC}"
echo ""

# Activate environment and upload
source .lerobot/bin/activate

huggingface-cli upload "${HF_USER}/${DATASET_NAME}" "$DATASET_DIR" --repo-type dataset

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Upload completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📊 Dataset Information:${NC}"
    echo "  - Repository: https://huggingface.co/datasets/${HF_USER}/${DATASET_NAME}"
    echo "  - Local path: $DATASET_DIR"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  - Train policy:   ./run/train_policy.sh -d ${DATASET_NAME}"
    echo "  - Visualize data: ./run/visualize_dataset.sh -d ${DATASET_NAME}"
else
    echo ""
    echo -e "${RED}❌ Upload failed. Please check the error messages above.${NC}"
    exit 1
fi