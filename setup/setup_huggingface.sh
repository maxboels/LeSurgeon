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

# Authenticate with Hugging Face
huggingface-cli login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authentication successful!${NC}"
echo ""

# Get and display user information
echo -e "${YELLOW}📊 Getting user information...${NC}"
HF_USER=$(huggingface-cli whoami | head -n 1)

if [ -z "$HF_USER" ]; then
    echo -e "${RED}❌ Failed to get user information${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Logged in as: $HF_USER${NC}"
echo ""

# Save user to environment
echo "# Hugging Face User (auto-generated)" >> "$(dirname "$0")/../.env"
echo "HF_USER=$HF_USER" >> "$(dirname "$0")/../.env"

echo -e "${BLUE}💾 User information saved to .env${NC}"
echo ""
echo -e "${GREEN}🎉 Setup complete! You can now use the recording and training scripts.${NC}"