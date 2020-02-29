# Harukaze

Repository holds code for the performance at the festival Harukaze in Tokyo, March 2019.

## How to run

From video and json:
```
python main.py --op-model-folder /home/ascent/openpose/models/ --data-path /home/ascent/harukaze/data --op-number-people-max 1 --op-render-pose 0 --op-net-resolution -1x256 --op-keypoint-scale 2 --no-inference
```

From video and openpose:
```
python main.py --op-model-folder /home/ascent/openpose/models/ --data-path /home/ascent/harukaze/data --op-number-people-max 1 --op-render-pose 0 --op-net-resolution -1x256 --op-keypoint-scale 2
```

From realsense and openpose:
```
python main.py --op-model-folder /home/ascent/openpose/models/ --op-number-people-max 1 --op-render-pose 0 --op-net-resolution -1x256 --op-keypoint-scale 2
```
