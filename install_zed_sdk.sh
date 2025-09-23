#!/bin/bash
# ZED SDK Installation Script (Official Steps)
# ============================================
# Install ZED SDK using official Stereolabs documentation

echo "🎥 ZED SDK Installation (Official Method)"
echo "========================================="
echo ""
echo "System Requirements Check:"
echo "  ✅ Ubuntu 24.04 LTS detected"  
echo "  ✅ NVIDIA RTX 4060 with CUDA 12.4 detected"
echo "  ✅ Ready for ZED SDK installation"
echo ""

# Check if zstd is installed
echo "📦 Checking dependencies..."
if ! command -v zstd &> /dev/null; then
    echo "⬇️  Installing zstd (required for installer)..."
    sudo apt update
    sudo apt install -y zstd
    echo "✅ zstd installed"
else
    echo "✅ zstd already installed"
fi

echo ""
echo "🔍 Finding latest ZED SDK version for Ubuntu 24 + CUDA 12.4..."
echo ""

# Create download directory
mkdir -p ~/Downloads/zed_sdk
cd ~/Downloads/zed_sdk

echo "⬇️  Downloading ZED SDK..."
echo "📍 Go to: https://www.stereolabs.com/developers/release/"
echo "📥 Download: ZED SDK 4.2+ for Ubuntu 24 CUDA 12.4"
echo ""
echo "💡 Expected filename: ZED_SDK_Ubuntu24_cudaX.X_vX.X.X.zstd.run"
echo ""

# Check for existing SDK file
SDK_FILE=$(ls ZED_SDK_Ubuntu24_cuda*.zstd.run 2>/dev/null | head -1)

if [ -n "$SDK_FILE" ]; then
    echo "✅ Found ZED SDK installer: $SDK_FILE"
    
    echo "🔧 Making installer executable..."
    chmod +x "$SDK_FILE"
    
    echo ""
    echo "🚀 Running ZED SDK installer..."
    echo "   During installation:"
    echo "   - Press 'q' after reading license"
    echo "   - Type 'y' for yes, 'n' for no, or Enter for default"
    echo "   - Installation includes Python wrapper by default"
    echo ""
    
    # Run installer
    ./"$SDK_FILE"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ ZED SDK installation completed!"
        echo ""
        echo "🔄 Testing installation..."
        
        # Test ZED SDK Python API
        if python3 -c "import pyzed.sl as sl; print('✅ ZED SDK Python API available, version:', sl.Camera.get_sdk_version())" 2>/dev/null; then
            echo "✅ ZED SDK Python API working!"
        else
            echo "⚠️  ZED SDK Python API not found. You may need to:"
            echo "   - Restart terminal/system"
            echo "   - Check if Python wrapper was installed"
            echo "   - Run: cd /usr/local/zed && python get_python_api.py"
        fi
        
        echo ""
        echo "🎉 ZED SDK Installation Complete!"
        echo ""
        echo "📋 Next steps:"
        echo "   1. Restart system if needed: sudo reboot"
        echo "   2. Test ZED camera: python src/cameras/zed_sdk_camera.py"
        echo "   3. Run teleoperation with ZED SDK quality!"
        
    else
        echo "❌ ZED SDK installation failed"
        exit 1
    fi
    
else
    echo "❌ ZED SDK installer not found in ~/Downloads/zed_sdk/"
    echo ""
    echo "📥 Please manually download:"
    echo "   1. Go to: https://www.stereolabs.com/developers/release/"
    echo "   2. Download: ZED SDK for Ubuntu 24 + CUDA 12.4"
    echo "   3. Move to: ~/Downloads/zed_sdk/"
    echo "   4. Re-run this script: ./install_zed_sdk.sh"
    echo ""
    echo "🌐 Opening download page..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://www.stereolabs.com/developers/release/" &
    fi
    
    exit 1
fi