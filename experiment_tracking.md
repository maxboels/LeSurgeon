# LeSurgeon Experiment Tracking - Surgical Suturing Task

## 📋 Experiment Overview

**Task**: Needle Picking and Needle Passing  
**Total Episodes**: 75 (5 demonstrations per needle position)
**Date Started**: September 22, 2025  
**Operator**: Maxence Boels  

### Task Description
The robot must perform a two-stage surgical suturing task:
1. **Needle Picking**: Grasp the needle with thread from its starting position on the suturing pad
2. **Needle Passing**: Transport the needle to the forceps/grasper position on the same suturing pad

### Equipment Setup
- **Suturing Pad**: Fixed position for all experiments
- **Needle with Thread**: Variable starting positions
- **Forceps/Grasper**: Variable positions on suturing pad
- **Clipper**: Attached to robot hand throughout all experiments

---

## 📍 Suturing Pad Grid Layout

```
Suturing Practice Pad (Top View)
┌─────────────────────────────┐
│   1     2     3     4     5 │
│                             │
│   6     7     8     9    10 │
│                             │
│  11    12    13    14    15 │
└─────────────────────────────┘
```

---

## 🎮 Recording Commands

Use these commands to record your episodes:

```bash
# Start recording session (adjust episode count for each phase)
./run/record_data.sh -n 10 -t "Needle picking and passing - Phase 1"
./run/record_data.sh -n 10 -t "Needle picking and passing - Phase 2" 
./run/record_data.sh -n 10 -t "Needle picking and passing - Phase 3"
./run/record_data.sh -n 10 -t "Needle picking and passing - Phase 4"
./run/record_data.sh -n 10 -t "Needle picking and passing - Phase 5"

# Check robot status before each session
./lesurgeon.sh status

# Start teleoperation with camera for positioning setup
./lesurgeon.sh teleop-cam
```

### Quick Setup Checklist (Before Each Episode)
- ☐ Suturing pad properly positioned
- ☐ Needle with thread placed at designated position
- ☐ Forceps/grasper placed at designated position  
- ☐ Robot clipper attached and functional
- ☐ Cameras positioned for optimal view
- ☐ Recording system ready
- ☐ Timer ready for duration tracking

---

**Experiment Log Created**: September 22, 2025  
**Last Updated**: _________________