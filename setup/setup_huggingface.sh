#!/bin/bash
# Hugging Face Authentication and Setup
# =====================================
# This script authenticates with Hugging Face and sets up user variables

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤗 Hugging Face Authentication Setup${NC}"
echo "====================================="
echo ""

# Check if .env file exists
if [ ! -f "$(dirname "$0")/../.env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with HUGGINGFACE_TOKEN"
    exit 1
fi

# Source environment variables
source "$(dirname "$0")/../.env"

# Check if token is set
if [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo -e "${RED}❌ HUGGINGFACE_TOKEN not set in .env file${NC}"
    exit 1
fi

echo -e "${YELLOW}📝 Authenticating with Hugging Face...${NC}"

# Activate LeRobot environment for CLI access
source "$(dirname "$0")/../.lerobot/bin/activate"

# Authenticate with Hugging Face
hf auth login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authentication successful!${NC}"
echo ""

# Get and display user information
echo -e "${YELLOW}📊 Getting user information...${NC}"
HF_USER=$(hf whoami 2>&1 | grep -E '^[a-zA-Z0-9._-]+$' | head -n 1 | tr -d '[:space:]')

if [ -z "$HF_USER" ]; then
    echo -e "${RED}❌ Failed to get user information${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Logged in as: $HF_USER${NC}"
echo ""

# Save user to environment (replace existing if present)
ENV_FILE="$(dirname "$0")/../.env"
if grep -q "^HF_USER=" "$ENV_FILE"; then
    # Replace existing HF_USER line
    sed -i "s/^HF_USER=.*/HF_USER=$HF_USER/" "$ENV_FILE"
else
    # Add new HF_USER line
    echo "" >> "$ENV_FILE"
    echo "# Hugging Face User (auto-generated)" >> "$ENV_FILE"
    echo "HF_USER=$HF_USER" >> "$ENV_FILE"
fi

echo -e "${BLUE}💾 User information saved to .env${NC}"
echo ""
echo -e "${GREEN}🎉 Setup complete! You can now use the recording and training scripts.${NC}"