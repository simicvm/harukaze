import os
import sys
import json
import argparse

import cv2
import numpy as np
import pyrealsense2 as rs

from pose import Pose, pose_points_from_json
from animation import Animation
from drawables import ChaserBall


inference_directory = 'data/pose_output/output'
inference_files = sorted([os.path.join(inference_directory, f) for f in os.listdir(inference_directory)])

cap = cv2.VideoCapture('data/ai_dance_short.MOV')


pose = Pose()
animation = Animation()
animation.add_pose(pose)

animation.objects.append(ChaserBall(pose.joints["right_hand"], x=300, y=300))
animation.objects.append(ChaserBall(pose.joints["head"], x=300, y=300))
animation.objects.append(ChaserBall(pose.joints["left_hand"], x=300, y=300))

i = 0
while(cap.isOpened()):
    print(i)
    # Capture frame-by-frame
    ret, frame = cap.read()
    width, height = frame.shape[:2]

    if ret == True:

        json_path = inference_files[i]

        pose_points = pose_points_from_json(json_path)
        if pose_points is not None:
            animation.update_pose(pose_points)

        # exit()

        # animation.update()
        frame = animation.draw_pose(frame)
        print(animation.pose)
        print(animation.pose.joints["right_hand"])

        animation.update()
        frame = animation.draw(frame)

        cv2.imshow('Frame', frame)

      # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break

    # Break the loop
    else:
        break

    i += 1

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
