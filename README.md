# Harukaze

Repository holds code for the performance at the festival Harukaze in Tokyo, March 2019.

## How to run

From video and json:
```
python main.py --op-model-folder /home/user/openpose/models/ --data-path /home/user/harukaze/data --op-number-people-max 1 --op-render-pose 0 --op-net-resolution 176x96 --op-output-resolution 1280x720 --op-keypoint-scale 2 --no-inference
```

From video and openpose:
```
python main.py --op-model-folder /home/user/openpose/models/ --data-path /home/user/harukaze/data --op-number-people-max 1 --op-render-pose 0 --op-net-resolution 176x96 --op-output-resolution 1280x720 --op-keypoint-scale 2
```

From realsense and openpose:
```
python main.py --op-model-folder /home/user/openpose/models/ --op-number-people-max 1 --op-render-pose 0 --op-net-resolution 176x96  --op-output-resolution 1280x720 --op-keypoint-scale 2
```
