# LeSurgeon Experiment Tracking - Surgical Suturing Task

## 📋 Experiment Overview

**Task**: Needle Picking and Needle Passing  
**Total Episodes**: 50  
**Date Started**: September 22, 2025  
**Operator**: [Your Name]  

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

## 🎯 Experiment Phases

### Phase 1: Fixed Positions (Episodes 1-10)
**Setup**: Needle and forceps positions are fixed for baseline performance
- Needle Position: Fixed at position A
- Forceps Position: Fixed at position B

### Phase 2: Variable Needle Position (Episodes 11-20)  
**Setup**: Needle position varies, forceps position remains fixed
- Needle Position: Variable (positions 1-10)
- Forceps Position: Fixed at position B

### Phase 3: Variable Forceps Position (Episodes 21-30)
**Setup**: Forceps position varies, needle position remains fixed  
- Needle Position: Fixed at position A
- Forceps Position: Variable (positions 1-10)

### Phase 4: Both Variable (Episodes 31-40)
**Setup**: Both needle and forceps positions vary
- Needle Position: Variable (brush pattern)
- Forceps Position: Variable (brush pattern)

### Phase 5: Advanced Scenarios (Episodes 41-50)
**Setup**: Complex positioning with increased difficulty
- Various challenging needle-forceps combinations
- Edge cases and corner positions

---

## 📍 Suturing Pad Grid Layout

```
Suturing Practice Pad (Top View - Brush Pattern Trajectory)
┌─────────────────────────────────────────────┐
│  1 ───→ 2 ───→ 3 ───→ 4 ───→ 5             │
│                               ↓             │
│  10 ←──── 9 ←─── 8 ←─── 7 ←─── 6             │
│  ↓                                           │
│  11 ───→ 12 ───→ 13 ───→ 14 ───→ 15         │
└─────────────────────────────────────────────┘

Position Legend:
- Numbers 1-15: Possible positions for needle/forceps placement
- Brush trajectory: 1→2→3→4→5→6→7→8→9→10→11→12→13→14→15
```

---

## ✅ Episode Tracking

### Phase 1: Fixed Positions (Baseline) - Episodes 1-10

| Episode | Needle Pos | Forceps Pos | Start Time | Duration | Success | Notes |
|---------|------------|-------------|------------|----------|---------|-------|
| 1 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 2 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 3 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 4 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 5 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 6 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 7 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 8 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 9 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 10 | A (Fixed) | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |

**Phase 1 Summary**: ___/10 successful episodes

### Phase 2: Variable Needle Position - Episodes 11-20

| Episode | Needle Pos | Forceps Pos | Start Time | Duration | Success | Notes |
|---------|------------|-------------|------------|----------|---------|-------|
| 11 | 1 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 12 | 2 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 13 | 3 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 14 | 4 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 15 | 5 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 16 | 6 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 17 | 7 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 18 | 8 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 19 | 9 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 20 | 10 | B (Fixed) | _________ | _______ | ☐ Pass ☐ Fail | _________________ |

**Phase 2 Summary**: ___/10 successful episodes

### Phase 3: Variable Forceps Position - Episodes 21-30

| Episode | Needle Pos | Forceps Pos | Start Time | Duration | Success | Notes |
|---------|------------|-------------|------------|----------|---------|-------|
| 21 | A (Fixed) | 11 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 22 | A (Fixed) | 12 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 23 | A (Fixed) | 13 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 24 | A (Fixed) | 14 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 25 | A (Fixed) | 15 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 26 | A (Fixed) | 1 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 27 | A (Fixed) | 2 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 28 | A (Fixed) | 3 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 29 | A (Fixed) | 4 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 30 | A (Fixed) | 5 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |

**Phase 3 Summary**: ___/10 successful episodes

### Phase 4: Both Variable - Episodes 31-40

| Episode | Needle Pos | Forceps Pos | Start Time | Duration | Success | Notes |
|---------|------------|-------------|------------|----------|---------|-------|
| 31 | 1 | 15 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 32 | 5 | 11 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 33 | 10 | 6 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 34 | 2 | 14 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 35 | 9 | 3 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 36 | 4 | 12 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 37 | 13 | 8 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 38 | 7 | 1 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 39 | 15 | 10 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 40 | 11 | 5 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |

**Phase 4 Summary**: ___/10 successful episodes

### Phase 5: Advanced Scenarios - Episodes 41-50

| Episode | Needle Pos | Forceps Pos | Start Time | Duration | Success | Notes |
|---------|------------|-------------|------------|----------|---------|-------|
| 41 | Corner-TL | Corner-BR | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 42 | Corner-TR | Corner-BL | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 43 | Edge-L | Edge-R | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 44 | Edge-T | Edge-B | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 45 | Center | Corner-TL | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 46 | Corner-BR | Center | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 47 | Random-1 | Random-1 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 48 | Random-2 | Random-2 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 49 | Challenge-1 | Challenge-1 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |
| 50 | Challenge-2 | Challenge-2 | _________ | _______ | ☐ Pass ☐ Fail | _________________ |

**Phase 5 Summary**: ___/10 successful episodes

---

## 📊 Overall Experiment Summary

### Success Rate by Phase
- **Phase 1** (Fixed): ___/10 (___%)
- **Phase 2** (Variable Needle): ___/10 (___%)  
- **Phase 3** (Variable Forceps): ___/10 (___%)
- **Phase 4** (Both Variable): ___/10 (___%)
- **Phase 5** (Advanced): ___/10 (___%)

**Total Success Rate**: ___/50 (___%)

### Performance Metrics
- **Average Episode Duration**: _______ seconds
- **Fastest Successful Episode**: _______ seconds (Episode #___)
- **Most Common Failure Mode**: _________________
- **Best Performing Phase**: _________________

### Key Observations
- _________________________________________________
- _________________________________________________
- _________________________________________________
- _________________________________________________

### Recommendations for Future Experiments
- _________________________________________________
- _________________________________________________
- _________________________________________________

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