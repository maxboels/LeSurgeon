#!/bin/bash
# LeSurgeon - Convenience Commands
# ===============================
# Quick access to common robotics tasks

set -e  # Exit on error

show_help() {
    echo "🤖 LeSurgeon Robot Commands"
    echo "=========================="
    echo ""
    echo "Environment:"
    echo "  activate     - Activate LeRobot environment"
    echo "  status       - Show robot calibration status"
    echo ""
    echo "Calibration:"
    echo "  calibrate    - Run robot calibration (interactive)"
    echo "  follower     - Calibrate follower arm only"
    echo "  leader       - Calibrate leader arm only"
    echo ""
    echo "Development:"
    echo "  wandb        - Setup Weights & Biases"
    echo "  test         - Test robot connection"
    echo ""
    echo "Usage: ./lesurgeon.sh <command>"
    echo ""
}

case "${1:-help}" in
    "activate")
        echo "🔧 Activating LeRobot environment..."
        source scripts/activate_lerobot.sh
        ;;
    
    "status")
        echo "📊 Checking robot status..."
        cd scripts && ./robot_status.sh && cd ..
        ;;
    
    "calibrate")
        echo "🔧 Running robot calibration..."
        source scripts/activate_lerobot.sh
        echo "Which robot would you like to calibrate?"
        echo "1) Follower arm"
        echo "2) Leader arm" 
        echo "3) Both arms"
        read -p "Enter choice (1-3): " choice
        
        case $choice in
            1) bash config/calibration.sh # Run follower section only
               ;;
            2) source .lerobot/bin/activate && lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=lesurgeon_leader_arm
               ;;
            3) bash config/calibration.sh # Run both sections
               ;;
            *) echo "Invalid choice"
               ;;
        esac
        ;;
    
    "follower")
        echo "🔧 Calibrating follower arm..."
        source .lerobot/bin/activate
        lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/ttyACM0 --robot.id=lesurgeon_follower_arm
        ;;
    
    "leader")
        echo "🔧 Calibrating leader arm..."
        source .lerobot/bin/activate
        lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/ttyACM0 --teleop.id=lesurgeon_leader_arm
        ;;
    
    "wandb")
        echo "📊 Setting up Weights & Biases..."
        source .lerobot/bin/activate
        python scripts/setup_wandb.py
        ;;
    
    "test")
        echo "🧪 Testing robot connection..."
        source .lerobot/bin/activate
        python -c "
try:
    from lerobot.robots.so101_follower import SO101Follower
    from lerobot.teleoperators.so101_leader import SO101Leader
    print('✅ Robot imports successful!')
    print('✅ LeRobot is working correctly!')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"
        ;;
    
    "help"|*)
        show_help
        ;;
esac