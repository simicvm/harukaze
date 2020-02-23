import cv2 
import json
import os

from pose import Pose, pose_points_from_json
from animation import Animation
from drawables import SpinningChaserBall, SpinningFixedBall, SpinningRandomBall

DRAW_POSE = False

inference_directory = '../data/pose_output/output'
inference_files = sorted([os.path.join(inference_directory, f) for f in os.listdir(inference_directory)])

cap = cv2.VideoCapture('../data/ai_dance_short.MOV') 

# create a new pose that contained Joint points that will live during the lenght of the program
pose = Pose()

# create an animation scene and attach the pose to it
animation = Animation()
animation.add_pose(pose)

# add a bunch of objects to the animation scene
animation.objects.append(SpinningChaserBall(x=300, y=300, chase_to=pose.joints["right_hand"], name="spinner_right"))
animation.objects.append(SpinningFixedBall(x=300, y=300, fixed_to=pose.joints["left_hand"], name="spinner_left"))
animation.objects.append(SpinningRandomBall(x=300, y=300, name="spinner_random"))


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

        if DRAW_POSE:
            animation.draw_pose(frame)

        animation.update()
        animation.draw(frame)

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
 