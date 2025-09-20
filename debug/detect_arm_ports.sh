#!/bin/bash
# ARM Port Detection Utility
# ==========================
# Automatically detects the /dev/ttyACM* ports for leader and follower arms
# based on their unique hardware serial numbers.

# Hardware serial numbers for each arm
LEADER_SERIAL="58FA101278"
FOLLOWER_SERIAL="5A46085090"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

detect_arm_ports() {
    local leader_port=""
    local follower_port=""
    
    echo -e "${BLUE}🔍 Detecting ARM ports based on serial numbers...${NC}"
    echo "Looking for:"
    echo "  - Leader arm serial:   ${LEADER_SERIAL}"
    echo "  - Follower arm serial: ${FOLLOWER_SERIAL}"
    echo ""
    
    # Check all ttyACM devices
    for device in /dev/ttyACM*; do
        if [ -c "$device" ]; then
            # Get the serial number for this device
            serial=$(udevadm info --name="$device" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
            
            if [ "$serial" = "$LEADER_SERIAL" ]; then
                leader_port="$device"
                echo -e "  ✅ ${GREEN}Leader arm found:   ${device} (serial: ${serial})${NC}"
            elif [ "$serial" = "$FOLLOWER_SERIAL" ]; then
                follower_port="$device"
                echo -e "  ✅ ${GREEN}Follower arm found: ${device} (serial: ${serial})${NC}"
            else
                echo -e "  ❓ ${YELLOW}Unknown device:     ${device} (serial: ${serial})${NC}"
            fi
        fi
    done
    
    echo ""
    
    # Validate results
    if [ -z "$leader_port" ]; then
        echo -e "${RED}❌ ERROR: Leader arm not found (serial: ${LEADER_SERIAL})${NC}"
        return 1
    fi
    
    if [ -z "$follower_port" ]; then
        echo -e "${RED}❌ ERROR: Follower arm not found (serial: ${FOLLOWER_SERIAL})${NC}"
        return 1
    fi
    
    # Export results
    export LEADER_PORT="$leader_port"
    export FOLLOWER_PORT="$follower_port"
    
    echo -e "${GREEN}🎯 Port Detection Results:${NC}"
    echo "  LEADER_PORT=$leader_port"
    echo "  FOLLOWER_PORT=$follower_port"
    echo ""
    
    return 0
}

# Function to get just the leader port
get_leader_port() {
    for device in /dev/ttyACM*; do
        if [ -c "$device" ]; then
            serial=$(udevadm info --name="$device" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
            if [ "$serial" = "$LEADER_SERIAL" ]; then
                echo "$device"
                return 0
            fi
        fi
    done
    return 1
}

# Function to get just the follower port
get_follower_port() {
    for device in /dev/ttyACM*; do
        if [ -c "$device" ]; then
            serial=$(udevadm info --name="$device" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
            if [ "$serial" = "$FOLLOWER_SERIAL" ]; then
                echo "$device"
                return 0
            fi
        fi
    done
    return 1
}

# If script is run directly, show detection results
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo -e "${BLUE}🤖 LeSurgeon ARM Port Detection${NC}"
    echo "=================================="
    echo ""
    
    if detect_arm_ports; then
        echo -e "${GREEN}✅ Both arms detected successfully!${NC}"
        echo ""
        echo "You can now use these environment variables in your scripts:"
        echo "  LEADER_PORT=$LEADER_PORT"
        echo "  FOLLOWER_PORT=$FOLLOWER_PORT"
        echo ""
        echo "Or source this script to use the detection functions:"
        echo "  source debug/detect_arm_ports.sh"
        echo "  LEADER=\$(get_leader_port)"
        echo "  FOLLOWER=\$(get_follower_port)"
    else
        echo -e "${RED}❌ ARM detection failed${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "1. Check that both arms are connected and powered"
        echo "2. Verify USB connections are secure"
        echo "3. Try unplugging and reconnecting both arms"
        exit 1
    fi
fi