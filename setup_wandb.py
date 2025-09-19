#!/usr/bin/env python3
"""
Weights & Biases (wandb) Setup Script for LeRobot
==================================================

This script helps you configure Weights & Biases for your LeRobot project.
"""

import wandb
import os
import sys

def setup_wandb():
    """Guide user through wandb setup process."""
    print("🤖 LeRobot - Weights & Biases Setup")
    print("=" * 40)
    print()
    
    # Check if already logged in
    try:
        api = wandb.Api()
        user = api.user()
        print("✅ You are already logged in to Weights & Biases!")
        print(f"   Logged in as: {user['username']}")
        print()
    except (wandb.errors.CommError, Exception):
        print("❌ Not logged in to Weights & Biases.")
        print()
        print("📋 Setup Steps:")
        print("1. Go to https://wandb.ai and create an account (if you don't have one)")
        print("2. Go to https://wandb.ai/authorize to get your API key")
        print("3. Run: wandb login")
        print("4. Enter your API key when prompted")
        print()
        
        # Ask if user wants to login now
        response = input("Would you like to login now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            try:
                wandb.login()
                print("✅ Successfully logged in!")
            except Exception as e:
                print(f"❌ Login failed: {e}")
                return False
        else:
            print("ℹ️  You can login later by running: wandb login")
            return False
    
    # Test wandb functionality
    print("🧪 Testing wandb functionality...")
    try:
        # Initialize a test run
        run = wandb.init(
            project="lerobot-test",
            name="setup-test",
            config={"test": True},
            mode="offline"  # Don't actually sync for the test
        )
        
        # Log some test metrics
        wandb.log({"test_metric": 42})
        
        # Finish the run
        wandb.finish()
        
        print("✅ Wandb test successful!")
        print()
        
    except Exception as e:
        print(f"❌ Wandb test failed: {e}")
        return False
    
    print("📊 Wandb Configuration Tips for LeRobot:")
    print("=" * 40)
    print("• Project naming: Use descriptive names like 'lerobot-aloha-training'")
    print("• Tags: Use tags like 'aloha', 'diffusion', 'training', etc.")
    print("• Group experiments: Use wandb.init(group='experiment-name')")
    print("• Log videos: wandb.log({'video': wandb.Video(video_path)})")
    print("• Save models: wandb.save('model.pt')")
    print()
    
    print("🎯 Example LeRobot Training Command:")
    print("python lerobot/scripts/train.py \\")
    print("  --config-path lerobot/configs/policy \\")
    print("  --config-name diffusion \\")
    print("  wandb.enable=true \\")
    print("  wandb.project=my-lerobot-project \\")
    print("  wandb.name=my-experiment")
    print()
    
    print("✨ Setup complete! Happy training with LeRobot! 🚀")
    return True

if __name__ == "__main__":
    setup_wandb()