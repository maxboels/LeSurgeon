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
    echo "  identify     - Identify which arm is leader/follower (interactive)"
    echo "  calibrate    - Run robot calibration (interactive)"
    echo "  follower     - Calibrate follower arm only"
    echo "  leader       - Calibrate leader arm only"
    echo ""
    echo "Operation:"
    echo "  teleoperate  - Start teleoperation session"
    echo "  teleop-auto  - Start teleoperation (auto-confirm calibration)"
    echo "  teleop-cam   - Start teleoperation with U20CAM-1080p camera"
    echo ""
    echo "Data & ML:"
    echo "  hf-setup     - Setup Hugging Face authentication"
    echo "  record       - Record teleoperation data for ML training"
    echo "  upload       - Upload dataset to Hugging Face Hub"
    echo "  train        - Train ML policy on recorded data"
    echo "  inference    - Run trained policy inference"
    echo "  replay       - Replay recorded episodes"
    echo "  visualize    - Visualize dataset"
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
        source setup/activate_lerobot.sh
        echo ""
        echo "⚠️  Note: The environment was activated during this script, but you're now back in your original shell."
        echo "To activate the environment in your current shell, run:"
        echo "   source setup/activate_lerobot.sh"
        echo ""
        ;;
    
    "identify")
        echo "🔍 Starting interactive arm identification..."
        bash setup/identify_arms_interactive.sh
        ;;
    
    "status")
        echo "📊 Checking robot status..."
        cd run && ./robot_status.sh && cd ..
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
            1) bash config/calibration.sh # Run follower section only (now with dynamic port detection)
               ;;
            2) # Leader only calibration with dynamic port detection
               source debug/detect_arm_ports.sh
               if detect_arm_ports; then
                   source .lerobot/bin/activate
                   lerobot-calibrate --teleop.type=so101_leader --teleop.port="$LEADER_PORT" --teleop.id=lesurgeon_leader_arm
               else
                   echo "❌ Failed to detect leader arm port"
               fi
               ;;
            3) bash config/calibration.sh # Run both sections (now with dynamic port detection)
               ;;
            *) echo "Invalid choice"
               ;;
        esac
        ;;
    
    "follower")
        echo "🔧 Calibrating follower arm with dynamic port detection..."
        source debug/detect_arm_ports.sh
        if detect_arm_ports; then
            source .lerobot/bin/activate
            lerobot-calibrate --robot.type=so101_follower --robot.port="$FOLLOWER_PORT" --robot.id=lesurgeon_follower_arm
        else
            echo "❌ Failed to detect follower arm port"
        fi
        ;;
    
    "leader")
        echo "🔧 Calibrating leader arm with dynamic port detection..."
        source debug/detect_arm_ports.sh
        if detect_arm_ports; then
            source .lerobot/bin/activate
            lerobot-calibrate --teleop.type=so101_leader --teleop.port="$LEADER_PORT" --teleop.id=lesurgeon_leader_arm
        else
            echo "❌ Failed to detect leader arm port"
        fi
        ;;
    
    "wandb")
        echo "📊 Setting up Weights & Biases..."
        source .lerobot/bin/activate
        python setup/setup_wandb.py
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
    
    "teleoperate")
        echo "🎮 Starting teleoperation session..."
        echo "Make sure both robots are connected and calibrated!"
        source .lerobot/bin/activate
        bash run/teleoperate.sh
        ;;
    
    "teleop-auto")
        echo "🎮 Starting teleoperation (auto-confirm)..."
        echo "Make sure both robots are connected and calibrated!"
        source .lerobot/bin/activate
        bash run/teleoperate_auto.sh
        ;;
    
    "teleop-cam")
        echo "🎮 Starting teleoperation with U20CAM-1080p camera..."
        echo "Make sure both robots and camera are connected!"
        source .lerobot/bin/activate
        bash run/teleoperate_with_camera.sh
        ;;
    
    "hf-setup")
        echo "🤗 Setting up Hugging Face authentication..."
        bash setup/setup_huggingface.sh
        ;;
    
    "record")
        echo "🎥 Starting data recording..."
        shift  # Remove the 'record' argument
        bash run/record_data.sh "$@"
        ;;
    
    "upload")
        echo "📤 Uploading dataset to Hugging Face..."
        shift  # Remove the 'upload' argument
        bash run/upload_dataset.sh "$@"
        ;;
    
    "train")
        echo "🧠 Starting policy training..."
        shift  # Remove the 'train' argument
        bash run/train_policy.sh "$@"
        ;;
    
    "inference")
        echo "🤖 Running policy inference..."
        shift  # Remove the 'inference' argument
        bash run/run_inference.sh "$@"
        ;;
    
    "replay")
        echo "🔄 Replaying episodes..."
        shift  # Remove the 'replay' argument
        bash run/replay_episodes.sh "$@"
        ;;
    
    "visualize")
        echo "📊 Visualizing dataset..."
        shift  # Remove the 'visualize' argument
        bash run/visualize_dataset.sh "$@"
        ;;
    
    "help"|*)
        show_help
        ;;
esac