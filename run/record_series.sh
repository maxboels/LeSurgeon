#!/bin/bash
# LeSurgeon Series Recording Script
# ================================
# Records multiple series of episodes for comprehensive dataset creation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_usage() {
    echo -e "${BLUE}🎥 LeSurgeon Series Recording${NC}"
    echo "============================"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -s, --series NUM       Number of series to record (default: 15)"
    echo "  -e, --episodes NUM     Episodes per series (default: 5)"
    echo "  -t, --task DESCRIPTION Base task description (default: 'Needle grasping and passing')"
    echo "  -d, --dataset NAME     Base dataset name (default: 'lesurgeon-suturing')"
    echo "  --start-from NUM       Start from series number (default: 1)"
    echo "  --separate-datasets    Create separate datasets for each series"
    echo "  --single-dataset       Use single dataset with series in task names (default)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Record 15 series, 5 episodes each"
    echo "  $0 -s 10 -e 3                        # Record 10 series, 3 episodes each"
    echo "  $0 --separate-datasets                # Create separate datasets per series"
    echo "  $0 --start-from 6                     # Resume from series 6"
    echo ""
    echo -e "${CYAN}Series Structure:${NC}"
    echo "  Single Dataset Mode: Episodes labeled as 'S01', 'S02', etc. in task description"
    echo "  Separate Dataset Mode: Datasets named 'dataset-s01', 'dataset-s02', etc."
}

# Default values
DEFAULT_NUM_SERIES=15
DEFAULT_EPISODES_PER_SERIES=5
DEFAULT_TASK="Needle grasping and passing"
DEFAULT_DATASET="lesurgeon-suturing"
DEFAULT_START_FROM=1
USE_SEPARATE_DATASETS=false

# Parse command line arguments
NUM_SERIES=$DEFAULT_NUM_SERIES
EPISODES_PER_SERIES=$DEFAULT_EPISODES_PER_SERIES
BASE_TASK="$DEFAULT_TASK"
BASE_DATASET="$DEFAULT_DATASET"
START_FROM=$DEFAULT_START_FROM

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--series)
            NUM_SERIES="$2"
            shift 2
            ;;
        -e|--episodes)
            EPISODES_PER_SERIES="$2"
            shift 2
            ;;
        -t|--task)
            BASE_TASK="$2"
            shift 2
            ;;
        -d|--dataset)
            BASE_DATASET="$2"
            shift 2
            ;;
        --start-from)
            START_FROM="$2"
            shift 2
            ;;
        --separate-datasets)
            USE_SEPARATE_DATASETS=true
            shift
            ;;
        --single-dataset)
            USE_SEPARATE_DATASETS=false
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🎥 LeSurgeon Series Recording${NC}"
echo "============================"
echo ""

# Display configuration
echo -e "${CYAN}📊 Series Recording Configuration:${NC}"
echo "  - Total Series:       $NUM_SERIES"
echo "  - Episodes per Series: $EPISODES_PER_SERIES"
echo "  - Starting from:      Series $START_FROM"
echo "  - Base Task:          $BASE_TASK"
echo "  - Base Dataset:       $BASE_DATASET"
if [ "$USE_SEPARATE_DATASETS" = true ]; then
    echo "  - Mode:               Separate datasets per series"
    echo "  - Dataset Pattern:    ${BASE_DATASET}-s01, ${BASE_DATASET}-s02, ..."
else
    echo "  - Mode:               Single dataset with series labels"
    echo "  - Dataset Name:       $BASE_DATASET"
fi
echo "  - Total Episodes:     $((NUM_SERIES * EPISODES_PER_SERIES))"
echo ""

# Confirm before starting
echo -e "${YELLOW}This will record $NUM_SERIES series with $EPISODES_PER_SERIES episodes each.${NC}"
echo -e "${YELLOW}Total: $((NUM_SERIES * EPISODES_PER_SERIES)) episodes${NC}"
echo ""
echo -e "${YELLOW}Start recording? (y/N)${NC}"
read -r confirmation
if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo "Recording cancelled."
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 Starting series recording...${NC}"
echo ""

# Record each series
CURRENT_SERIES=$START_FROM
TOTAL_RECORDED=0
FAILED_SERIES=()

while [ $CURRENT_SERIES -le $NUM_SERIES ]; do
    SERIES_NUM=$(printf "%02d" $CURRENT_SERIES)
    
    echo -e "${BLUE}📹 Recording Series $SERIES_NUM ($CURRENT_SERIES/$NUM_SERIES)${NC}"
    echo "============================================="
    
    if [ "$USE_SEPARATE_DATASETS" = true ]; then
        # Separate dataset for each series
        DATASET_NAME="${BASE_DATASET}-s${SERIES_NUM}"
        TASK_DESC="$BASE_TASK - Series $SERIES_NUM"
        RESUME_FLAG=""
    else
        # Single dataset with series in task name
        DATASET_NAME="$BASE_DATASET"
        TASK_DESC="S${SERIES_NUM} - $BASE_TASK"
        if [ $CURRENT_SERIES -eq $START_FROM ]; then
            RESUME_FLAG=""
        else
            RESUME_FLAG="-r"
        fi
    fi
    
    echo -e "${CYAN}Series Details:${NC}"
    echo "  - Series:   $SERIES_NUM"
    echo "  - Dataset:  $DATASET_NAME"
    echo "  - Task:     $TASK_DESC"
    echo "  - Episodes: $EPISODES_PER_SERIES"
    echo ""
    
    # Run the recording
    if bash "$(dirname "$0")/record_data.sh" $RESUME_FLAG -d "$DATASET_NAME" -n "$EPISODES_PER_SERIES" -t "$TASK_DESC"; then
        echo -e "${GREEN}✅ Series $SERIES_NUM completed successfully!${NC}"
        TOTAL_RECORDED=$((TOTAL_RECORDED + EPISODES_PER_SERIES))
    else
        echo -e "${RED}❌ Series $SERIES_NUM failed!${NC}"
        FAILED_SERIES+=($SERIES_NUM)
    fi
    
    echo ""
    echo -e "${BLUE}Progress: $CURRENT_SERIES/$NUM_SERIES series completed${NC}"
    echo -e "${BLUE}Episodes recorded so far: $TOTAL_RECORDED${NC}"
    echo ""
    
    # Ask if user wants to continue (except for the last series)
    if [ $CURRENT_SERIES -lt $NUM_SERIES ]; then
        echo -e "${YELLOW}Continue to Series $(printf "%02d" $((CURRENT_SERIES + 1)))? (Y/n)${NC}"
        read -r continue_choice
        if [[ "$continue_choice" =~ ^[Nn]$ ]]; then
            echo "Recording stopped by user."
            break
        fi
    fi
    
    CURRENT_SERIES=$((CURRENT_SERIES + 1))
done

echo ""
echo -e "${GREEN}🎉 Series recording session completed!${NC}"
echo "======================================"
echo ""

# Display summary
echo -e "${CYAN}📊 Recording Summary:${NC}"
echo "  - Series completed: $((CURRENT_SERIES - START_FROM))"
echo "  - Total episodes:   $TOTAL_RECORDED"
if [ ${#FAILED_SERIES[@]} -eq 0 ]; then
    echo -e "${GREEN}  - All series successful! ✅${NC}"
else
    echo -e "${YELLOW}  - Failed series: ${FAILED_SERIES[*]}${NC}"
fi
echo ""

if [ "$USE_SEPARATE_DATASETS" = true ]; then
    echo -e "${BLUE}📤 Next Steps:${NC}"
    echo "Upload individual series datasets:"
    for ((i=START_FROM; i<=CURRENT_SERIES-1; i++)); do
        SERIES_NUM=$(printf "%02d" $i)
        echo "  ./lesurgeon.sh upload -d ${BASE_DATASET}-s${SERIES_NUM}"
    done
else
    echo -e "${BLUE}📤 Next Steps:${NC}"
    echo "  - Upload dataset: ./lesurgeon.sh upload -d $BASE_DATASET"
    echo "  - Train policy:   ./lesurgeon.sh train -d $BASE_DATASET"
    echo "  - Visualize data: ./lesurgeon.sh visualize -d $BASE_DATASET"
fi
echo ""
echo -e "${GREEN}Happy robot learning! 🚀${NC}"