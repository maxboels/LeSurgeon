#!/bin/bash
# ARM Identification Status and Verification
# ==========================================
# Shows current arm identification status and verifies the configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

CONFIG_FILE="$(dirname "$0")/arm_mapping.conf"
DETECTION_SCRIPT="$(dirname "$0")/../debug/detect_arm_ports.sh"

echo -e "${BOLD}${BLUE}🤖 LeSurgeon ARM Identification Status${NC}"
echo "======================================="
echo ""

# Check if configuration file exists
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✅ Arm mapping configuration found${NC}"
    echo -e "${CYAN}Configuration file: $CONFIG_FILE${NC}"
    echo ""
    
    # Source the configuration
    source "$CONFIG_FILE"
    
    echo -e "${BOLD}Current Configuration:${NC}"
    echo "- LEADER Serial: $LEADER_SERIAL"
    echo "- FOLLOWER Serial: $FOLLOWER_SERIAL"
    echo ""
    
    # Show when it was created
    if [ -f "$CONFIG_FILE" ]; then
        config_date=$(stat -c %y "$CONFIG_FILE" 2>/dev/null || stat -f %Sm "$CONFIG_FILE" 2>/dev/null || echo "Unknown")
        echo "Configuration created: $config_date"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  No arm mapping configuration found${NC}"
    echo "   Run: ./lesurgeon.sh identify"
    echo "   Or:  ./debug/identify_arms_interactive.sh"
    echo ""
fi

# Check current connected devices
echo -e "${BOLD}${BLUE}Currently Connected Devices:${NC}"
connected_devices=()
for device in /dev/ttyACM*; do
    if [ -c "$device" ]; then
        serial=$(udevadm info --name="$device" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
        if [ -n "$serial" ]; then
            connected_devices+=("$device:$serial")
            echo "- $device (Serial: $serial)"
        fi
    fi
done

if [ ${#connected_devices[@]} -eq 0 ]; then
    echo -e "${YELLOW}No ARM devices currently connected${NC}"
fi
echo ""

# Test current detection if both config and script exist
if [ -f "$CONFIG_FILE" ] && [ -f "$DETECTION_SCRIPT" ]; then
    echo -e "${BOLD}${BLUE}Testing Current Detection:${NC}"
    
    # Source the detection script
    source "$DETECTION_SCRIPT"
    
    if detect_arm_ports; then
        echo -e "${GREEN}✅ Detection successful!${NC}"
        echo ""
        echo -e "${BOLD}Detected Mappings:${NC}"
        echo "- LEADER Port: $LEADER_PORT"
        echo "- FOLLOWER Port: $FOLLOWER_PORT"
        
        # Cross-reference with configuration
        if [ -f "$CONFIG_FILE" ]; then
            echo ""
            echo -e "${BOLD}Verification:${NC}"
            
            # Check leader
            leader_device_serial=$(udevadm info --name="$LEADER_PORT" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
            if [ "$leader_device_serial" = "$LEADER_SERIAL" ]; then
                echo -e "- Leader mapping: ${GREEN}✅ CORRECT${NC}"
            else
                echo -e "- Leader mapping: ${RED}❌ MISMATCH${NC} (Expected: $LEADER_SERIAL, Found: $leader_device_serial)"
            fi
            
            # Check follower
            follower_device_serial=$(udevadm info --name="$FOLLOWER_PORT" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
            if [ "$follower_device_serial" = "$FOLLOWER_SERIAL" ]; then
                echo -e "- Follower mapping: ${GREEN}✅ CORRECT${NC}"
            else
                echo -e "- Follower mapping: ${RED}❌ MISMATCH${NC} (Expected: $FOLLOWER_SERIAL, Found: $follower_device_serial)"
            fi
        fi
    else
        echo -e "${RED}❌ Detection failed${NC}"
        echo "This could mean:"
        echo "1. One or both arms are not connected"
        echo "2. Arms need to be re-identified"
        echo "3. Configuration is incorrect"
    fi
    echo ""
fi

echo -e "${BOLD}${CYAN}Available Commands:${NC}"
echo "- ./lesurgeon.sh identify    - Run interactive arm identification"
echo "- ./lesurgeon.sh status      - Check robot calibration status"
echo "- ./lesurgeon.sh teleop-cam  - Start teleoperation with camera"
echo ""

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${BOLD}${YELLOW}⚠️  Recommendation: Run arm identification first${NC}"
    echo "   ./lesurgeon.sh identify"
fi