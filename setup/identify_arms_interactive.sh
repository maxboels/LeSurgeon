#!/bin/bash
# Interactive ARM Identification Script
# =====================================
# This script helps you identify which physical arm corresponds to which role
# by connecting them one at a time and mapping their serial numbers correctly.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration file to store the mapping
CONFIG_FILE="$(dirname "$0")/arm_mapping.conf"

echo -e "${BOLD}${BLUE}🤖 LeSurgeon ARM Identification Wizard${NC}"
echo "========================================"
echo ""
echo "This script will help you identify which physical arm is the LEADER and which is the FOLLOWER"
echo "by connecting them one at a time. This ensures we never mix them up again!"
echo ""

# Function to wait for user input
wait_for_enter() {
    echo -e "${CYAN}Press ENTER to continue...${NC}"
    read -r
}

# Function to get all connected ttyACM devices with their serials
get_connected_devices() {
    local devices=()
    for device in /dev/ttyACM*; do
        if [ -c "$device" ]; then
            serial=$(udevadm info --name="$device" --query=property | grep "ID_USB_SERIAL_SHORT=" | cut -d'=' -f2)
            if [ -n "$serial" ]; then
                devices+=("$device:$serial")
            fi
        fi
    done
    printf '%s\n' "${devices[@]}"
}

# Function to detect changes in connected devices
detect_device_changes() {
    local before=("$@")
    local after=($(get_connected_devices))
    
    # Find devices in 'after' that weren't in 'before'
    for device_after in "${after[@]}"; do
        local found=false
        for device_before in "${before[@]}"; do
            if [ "$device_after" = "$device_before" ]; then
                found=true
                break
            fi
        done
        if [ "$found" = false ]; then
            echo "$device_after"
            return 0
        fi
    done
    return 1
}

echo -e "${YELLOW}⚠️  IMPORTANT: Please DISCONNECT both arms before starting${NC}"
echo ""
echo "1. Unplug both robot arms from USB"
echo "2. Make sure no /dev/ttyACM* devices are connected to the arms"
echo ""

# Check that no arms are currently connected
current_devices=($(get_connected_devices))
if [ ${#current_devices[@]} -gt 0 ]; then
    echo -e "${RED}❌ Detected the following devices still connected:${NC}"
    for device in "${current_devices[@]}"; do
        IFS=':' read -r port serial <<< "$device"
        echo "   - $port (serial: $serial)"
    done
    echo ""
    echo -e "${YELLOW}Please disconnect all arms and run this script again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Good! No arm devices detected.${NC}"
echo ""

# Step 1: Identify the LEADER arm
echo -e "${BOLD}${BLUE}Step 1: Identify the LEADER ARM${NC}"
echo "================================"
echo ""
echo "The LEADER arm is the one you will use to control the FOLLOWER arm."
echo "It's typically the arm you hold and manipulate during teleoperation."
echo ""
echo -e "${CYAN}Please connect ONLY the LEADER arm now.${NC}"
echo ""

wait_for_enter

# Wait for a device to appear
echo -e "${YELLOW}⏳ Waiting for LEADER arm to be detected...${NC}"
leader_device=""
for i in {1..10}; do
    sleep 1
    devices_now=($(get_connected_devices))
    if [ ${#devices_now[@]} -eq 1 ]; then
        leader_device="${devices_now[0]}"
        break
    elif [ ${#devices_now[@]} -gt 1 ]; then
        echo -e "${RED}❌ Multiple devices detected! Please connect only ONE arm.${NC}"
        exit 1
    fi
    echo -n "."
done

if [ -z "$leader_device" ]; then
    echo -e "${RED}❌ No device detected. Please check the connection and try again.${NC}"
    exit 1
fi

IFS=':' read -r leader_port leader_serial <<< "$leader_device"
echo ""
echo -e "${GREEN}✅ LEADER arm detected!${NC}"
echo "   Port: $leader_port"
echo "   Serial: $leader_serial"
echo ""

# Step 2: Identify the FOLLOWER arm
echo -e "${BOLD}${BLUE}Step 2: Identify the FOLLOWER ARM${NC}"
echo "================================="
echo ""
echo "The FOLLOWER arm is the one that will mimic the movements of the LEADER arm."
echo "It's the arm that performs the actual tasks during teleoperation."
echo ""
echo -e "${CYAN}Please connect the FOLLOWER arm now (keep the LEADER connected).${NC}"
echo ""

wait_for_enter

# Wait for the second device to appear
echo -e "${YELLOW}⏳ Waiting for FOLLOWER arm to be detected...${NC}"
follower_device=""
for i in {1..10}; do
    sleep 1
    devices_now=($(get_connected_devices))
    if [ ${#devices_now[@]} -eq 2 ]; then
        # Find the device that's not the leader
        for device in "${devices_now[@]}"; do
            if [ "$device" != "$leader_device" ]; then
                follower_device="$device"
                break
            fi
        done
        break
    elif [ ${#devices_now[@]} -gt 2 ]; then
        echo -e "${RED}❌ Too many devices detected! Please connect only the two arms.${NC}"
        exit 1
    elif [ ${#devices_now[@]} -eq 1 ]; then
        echo -n "."
    fi
done

if [ -z "$follower_device" ]; then
    echo -e "${RED}❌ FOLLOWER device not detected. Please check the connection and try again.${NC}"
    exit 1
fi

IFS=':' read -r follower_port follower_serial <<< "$follower_device"
echo ""
echo -e "${GREEN}✅ FOLLOWER arm detected!${NC}"
echo "   Port: $follower_port"
echo "   Serial: $follower_serial"
echo ""

# Step 3: Save the configuration
echo -e "${BOLD}${BLUE}Step 3: Saving Configuration${NC}"
echo "============================="
echo ""
echo -e "${CYAN}Identified arms:${NC}"
echo ""
echo -e "${BOLD}LEADER ARM${NC} (the one you control):"
echo "   Port: $leader_port"
echo "   Serial: $leader_serial"
echo ""
echo -e "${BOLD}FOLLOWER ARM${NC} (the one that mimics):"
echo "   Port: $follower_port" 
echo "   Serial: $follower_serial"
echo ""
echo -e "${BLUE}💾 Saving arm identification...${NC}"

cat > "$CONFIG_FILE" << EOF
# LeSurgeon ARM Identification Configuration
# Generated on $(date)
# This file maps physical arms to their roles based on interactive identification

LEADER_SERIAL="$leader_serial"
FOLLOWER_SERIAL="$follower_serial"

# Original detection results:
# LEADER ARM - Port: $leader_port, Serial: $leader_serial
# FOLLOWER ARM - Port: $follower_port, Serial: $follower_serial
EOF

echo -e "${GREEN}✅ Configuration saved to: $CONFIG_FILE${NC}"
echo ""

# Step 4: Test the configuration
echo -e "${BOLD}${BLUE}Step 4: Testing the new configuration${NC}"
echo "======================================"
echo ""
echo -e "${CYAN}Let's test the new identification by running the port detection...${NC}"
echo ""

# Update the detect_arm_ports.sh script to use our new configuration
detection_script="$(dirname "$0")/../debug/detect_arm_ports.sh"
if [ -f "$detection_script" ]; then
    echo -e "${BLUE}📝 Updating port detection script...${NC}"
    
    # Backup the original
    cp "$detection_script" "${detection_script}.backup"
    
    # Update the serial numbers in the detection script
    sed -i "s/LEADER_SERIAL=\".*\"/LEADER_SERIAL=\"$leader_serial\"/" "$detection_script"
    sed -i "s/FOLLOWER_SERIAL=\".*\"/FOLLOWER_SERIAL=\"$follower_serial\"/" "$detection_script"
    
    echo -e "${GREEN}✅ Port detection script updated${NC}"
    echo -e "${YELLOW}📄 Backup saved as: ${detection_script}.backup${NC}"
else
    echo -e "${YELLOW}⚠️  Port detection script not found at: $detection_script${NC}"
fi

echo ""
echo "Testing current detection:"
source "$detection_script"

if detect_arm_ports; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Arm identification completed successfully!${NC}"
    echo ""
    echo -e "${BOLD}Configuration Summary:${NC}"
    echo "- LEADER ARM (controller): Serial $leader_serial → Port $LEADER_PORT"
    echo "- FOLLOWER ARM (mimic): Serial $follower_serial → Port $FOLLOWER_PORT"
    echo ""
    echo -e "${CYAN}You can now use ./lesurgeon.sh teleop-cam with confidence!${NC}"
else
    echo -e "${RED}❌ Testing failed. Please check the connections and try again.${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}${GREEN}🤖 ARM Identification Complete! 🤖${NC}"