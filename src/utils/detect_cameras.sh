#!/bin/bash
# Camera Detection and Configuration Utility
# ===========================================
# Automatically detects available cameras and sets optimal configurations

# Check if ZED 2 camera is available
detect_zed_camera() {
    # Check for ZED via v4l2 devices (more reliable)
    if v4l2-ctl --list-devices 2>/dev/null | grep -q "ZED"; then
        if [ -c "/dev/video2" ]; then
            echo "true"
            return 0
        fi
    fi
    echo "false"
    return 1
}

# Check if U20CAM is available
detect_u20cam() {
    # Check for U20CAM via v4l2 devices (more reliable than lsusb)
    if v4l2-ctl --list-devices 2>/dev/null | grep -q "U20CAM\|Innomaker"; then
        if [ -c "/dev/video0" ]; then
            echo "true"
            return 0
        fi
    fi
    echo "false"
    return 1
}

# Get optimal camera configuration
get_camera_config() {
    local zed_available=$(detect_zed_camera)
    local u20cam_available=$(detect_u20cam)
    
    echo "# Camera Detection Results" >&2
    echo "ZED_AVAILABLE=\"$zed_available\"" >&2
    echo "U20CAM_AVAILABLE=\"$u20cam_available\"" >&2
    
    if [[ "$zed_available" == "true" && "$u20cam_available" == "true" ]]; then
        # Best setup: U20CAM for close-up wrist view, ZED multi-modal for spatial awareness
        echo "CAMERA_CONFIG=\"{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, zed_left: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}, zed_stereo: {type: opencv, index_or_path: /dev/video2, width: 2560, height: 720, fps: 30}}\""
        echo "CAMERA_DESCRIPTION=\"U20CAM (wrist) + ZED 2 Multi-Modal (left eye + stereo depth)\""
        echo "CAMERA_MODE=\"hybrid\""
    elif [[ "$zed_available" == "true" ]]; then
        # ZED multi-modal: Left eye + right eye + stereo for depth
        echo "CAMERA_CONFIG=\"{ left_eye: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}, right_eye: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}, stereo_depth: {type: opencv, index_or_path: /dev/video2, width: 2560, height: 720, fps: 30}}\""
        echo "CAMERA_DESCRIPTION=\"ZED 2 Multi-Modal (stereo RGB + depth + point clouds)\""
        echo "CAMERA_MODE=\"zed_multimodal\""
    elif [[ "$u20cam_available" == "true" ]]; then
        # Fallback to dual U20CAM setup
        echo "CAMERA_CONFIG=\"{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, external: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}}\""
        echo "CAMERA_DESCRIPTION=\"U20CAM Dual Setup (standard RGB)\""
        echo "CAMERA_MODE=\"standard\""
    else
        # No cameras detected
        echo "CAMERA_CONFIG=\"\""
        echo "CAMERA_DESCRIPTION=\"No compatible cameras detected\""
        echo "CAMERA_MODE=\"none\""
        return 1
    fi
    
    return 0
}

# Export camera configuration for use in other scripts
export_camera_config() {
    local config_output=$(get_camera_config 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        eval "$config_output"
        export CAMERA_CONFIG
        export CAMERA_DESCRIPTION
        export CAMERA_MODE
        return 0
    else
        export CAMERA_CONFIG=""
        export CAMERA_DESCRIPTION="No compatible cameras detected"
        export CAMERA_MODE="none"
        return 1
    fi
}

# Main function for standalone usage
main() {
    echo "🔍 Camera Detection Utility"
    echo "============================"
    
    local zed_available=$(detect_zed_camera)
    local u20cam_available=$(detect_u20cam)
    
    echo ""
    echo "Available Cameras:"
    echo "  ZED 2 Stereo: $zed_available"
    echo "  U20CAM:       $u20cam_available"
    echo ""
    
    if get_camera_config >/dev/null; then
        local config_output=$(get_camera_config 2>/dev/null)
        eval "$config_output"
        
        echo "Recommended Configuration:"
        echo "  Description: $CAMERA_DESCRIPTION"
        echo "  Config: $CAMERA_CONFIG"
    else
        echo "❌ No compatible camera configuration found"
        return 1
    fi
}

# If script is run directly, show detection results
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi