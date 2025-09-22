# LeSurgeon Dataset - Surgical Needle Manipulation

<!-- Provide a quick summary of the dataset. -->

This dataset contains robotic teleoperation demonstrations for surgical needle manipulation tasks, collected using the LeRobot framework with dual SO-ARM101 robotic arms in a leader-follower configuration.

## Dataset Details

### Dataset Description

<!-- Provide a longer summary of what this dataset is. -->

**LeSurgeon** is a robotics dataset focused on surgical needle manipulation tasks, specifically needle grasping and passing motions. The dataset was collected using a dual-arm setup with leader-follower teleoperation, where human demonstrations guide a follower robot arm through precise surgical motions. This dataset is designed for training imitation learning policies for robotic surgical assistance.

- **Curated by:** Maxboels
- **Language(s) (NLP):** N/A (Robotics dataset)
- **License:** Apache 2.0

### Dataset Sources

<!-- Provide the basic links for the dataset. -->

- **Repository:** https://github.com/maxboels/LeSurgeon
- **Paper:** [Coming Soon]
- **Demo:** [Optional link to demo]

## Uses

<!-- Address questions around how the dataset is intended to be used. -->

### Direct Use

<!-- This section describes suitable use cases for the dataset. -->

This dataset is intended for:
- Training imitation learning policies for robotic surgical tasks
- Research in surgical robotics and autonomous manipulation
- Benchmarking robotic learning algorithms on precise manipulation tasks
- Educational purposes in robotics and machine learning

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the dataset will not work well for. -->

This dataset should not be used for:
- Direct medical procedures without proper validation and regulatory approval
- Commercial surgical applications without extensive testing and certification
- Training on tasks significantly different from needle manipulation
- Real-time surgical applications without safety verification

## Dataset Structure

<!-- This section provides a description of the dataset fields, and additional information about the dataset structure such as criteria used to create the splits, relationships between data points, etc. -->

### Data Instances

Each data instance represents a single frame in a teleoperation episode, containing:
- Robot joint positions (action and observation)
- Dual camera images (wrist-mounted and external view)
- Temporal information (timestamps, frame indices)

### Data Fields

- **action**: [6] float32 - Joint position commands for the follower arm
- **observation.state**: [6] float32 - Current joint positions of the follower arm
- **observation.images.wrist**: [720, 1280, 3] uint8 - End-effector mounted camera view
- **observation.images.external**: [720, 1280, 3] uint8 - External workspace camera view
- **timestamp**: [1] float32 - Episode timestamp in seconds
- **frame_index**: [1] int64 - Frame number within the current episode
- **episode_index**: [1] int64 - Episode identifier (0-49 for 50 episodes)
- **index**: [1] int64 - Global frame index across all episodes
- **task_index**: [1] int64 - Task identifier (always 0 for single task)

### Data Splits

The dataset contains a single training split with 50 episodes of needle manipulation demonstrations.

| Split | Episodes |
|-------|----------|
| train | 50       |

## Dataset Creation

### Curation Rationale

<!-- Motivation for the creation of this dataset. -->

This dataset was created to advance research in surgical robotics, specifically focusing on precise manipulation tasks that require high dexterity and spatial awareness. Needle manipulation is a fundamental skill in surgery, making it an ideal benchmark task for robotic learning systems.

### Source Data

<!-- This section describes the source data (e.g. news text and headlines, social media posts, translated sentences, ...). -->

#### Data Collection and Processing

<!-- This section describes the data collection and processing process such as data selection criteria, filtering and normalization methods, tools and libraries used, etc. -->

**Hardware Setup:**
- **Leader Arm:** SO-ARM101 (Serial: 58FA101278) - Human operator control
- **Follower Arm:** SO-ARM101 (Serial: 5A46085090) - Learning/execution robot
- **Cameras:** Dual U20CAM-1080p cameras at 720p @ 30fps
  - Wrist camera: /dev/video0 (end-effector view)
  - External camera: /dev/video2 (workspace overview)

**Collection Protocol:**
1. Environment setup with standardized surgical workspace and consistent lighting
2. Robot calibration ensuring precise leader-follower mapping
3. Human demonstration of needle manipulation tasks via teleoperation
4. Synchronized recording of joint states and dual camera feeds at 30Hz
5. Episode validation for task completion and data quality

#### Who are the source data producers?

<!-- This section describes the people or systems who originally created the data. It should also include self-reported demographic or identity information for the source data creators if this information is available. -->

The source data was produced by human operators performing teleoperated demonstrations using the leader robot arm. The demonstrations were collected in a controlled laboratory environment by robotics researchers.

### Annotations

<!-- If the dataset contains annotations which are not part of the initial data collection, use this section to describe them. -->

#### Annotation process

<!-- This section describes the annotation process such as annotation tools used in the process, the amount of data annotated, annotation guidelines provided to the annotators, interannotator statistics, annotation validation, etc. -->

No additional annotations were added beyond the intrinsic labels provided by the teleoperation system (joint positions, camera images, and temporal information).

#### Who are the annotators?

<!-- This section describes the people or systems who created the annotations. -->

N/A - Dataset contains only teleoperation demonstrations without additional annotations.

#### Personal and Sensitive Information

<!-- State whether the dataset contains data that might be considered personal, sensitive, or private (e.g., data that reveals addresses, uniquely identifiable names or aliases, racial or ethnic origins, sexual orientations, religious beliefs, political opinions, financial or health data, etc.). If efforts were made to anonymize the data, describe the anonymization process. -->

This dataset does not contain any personal or sensitive information. All data consists of robot sensor readings and camera images of the workspace without any human subjects or identifiable information.

## Bias, Risks, and Limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

### Limitations

- Limited to a single task type (needle manipulation)
- Collected in a controlled laboratory environment
- Single human demonstrator may introduce individual biases in technique
- Limited diversity in needle types, workspace configurations, and lighting conditions
- 50 episodes may be insufficient for complex policy learning without data augmentation

### Risks

- Policies trained on this data should not be deployed in real surgical environments without extensive validation
- The controlled laboratory setup may not generalize to real clinical conditions
- Limited robustness testing across different environmental conditions

### Recommendations

<!-- This section is meant to convey recommendations with respect to the bias, risk, and technical limitations. -->

Users should:
- Validate any trained policies extensively before considering real-world deployment
- Combine with additional datasets for improved robustness
- Implement appropriate safety measures and human oversight
- Consider the limitations of single-demonstrator data when interpreting results

## Citation

<!-- If there is a paper or blog post introducing the dataset, the APA and Bibtex information for that should go in this section. -->

**BibTeX:**

```bibtex
@dataset{lesurgeon2025,
  title={LeSurgeon: A Surgical Robotics Dataset for Needle Manipulation},
  author={Maxboels},
  year={2025},
  url={https://huggingface.co/datasets/maxboels/lesurgeon-s01},
  note={Dataset created using LeRobot framework}
}
```

**APA:**

Maxboels. (2025). *LeSurgeon: A Surgical Robotics Dataset for Needle Manipulation* [Dataset]. Hugging Face. https://huggingface.co/datasets/maxboels/lesurgeon-s01

## Glossary

<!-- If relevant, include terms and calculations in this section that can help readers understand the dataset or dataset card. -->

- **LeRobot**: Open-source robotics framework for data collection and policy learning
- **Leader-Follower**: Teleoperation setup where human controls leader arm, follower arm mimics movements
- **Episode**: Complete demonstration sequence from task start to completion
- **Action Space**: 6-DOF robot joint configuration (shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper)
- **Observation Space**: Combined sensor data including joint positions and camera images

## More Information

<!-- If there is additional information that is not covered in the above sections, include it here. -->

### Technical Specifications

- **Recording Frequency:** 30 Hz
- **Episode Duration:** 60 seconds maximum
- **Reset Time:** 30 seconds between episodes
- **Action Space:** 6-DOF continuous control
- **Observation Space:** Joint positions + dual RGB cameras
- **File Format:** LeRobot-compatible Parquet files with MP4 video streams

### Usage Example

```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset

# Load dataset
dataset = LeRobotDataset("maxboels/lesurgeon-s01")

# Access first episode
episode_0 = dataset[0]
print(f"Action shape: {episode_0['action'].shape}")
print(f"Wrist camera shape: {episode_0['observation.images.wrist'].shape}")

# Iterate through episodes
for i, data in enumerate(dataset):
    if i >= 10:  # First 10 frames
        break
    print(f"Frame {i}: Action={data['action']}, Timestamp={data['timestamp']}")
```

### Related Work

- [LeRobot Framework](https://github.com/huggingface/lerobot)
- [SO-ARM101 Robot Documentation](https://github.com/TheRobotStudio/SO-ARM101)
- [ACT: Action Chunking with Transformers](https://arxiv.org/abs/2304.13705)

## Dataset Card Authors

Maxboels

## Dataset Card Contact

For questions or issues regarding this dataset, please open an issue in the [GitHub repository](https://github.com/maxboels/LeSurgeon).