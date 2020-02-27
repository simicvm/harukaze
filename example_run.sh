#!/bin/bash
python main.py --op-model-folder /home/ascent/openpose/models/ --data-file /home/ascent/harukaze/data/ai_office_dance.avi --op-number-people-max 1 --op-render-pose 0 --op-net-resolution -1x256 --op-output-resolution 1280x720 --op-keypoint-scale 2
