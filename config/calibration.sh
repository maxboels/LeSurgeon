


# Follower
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=lesurgeon_follower_arm # <- Give the robot a unique name



# Leader
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM0 \
    --teleop.id=lesurgeon_leader_arm # <- Give the robot a unique name