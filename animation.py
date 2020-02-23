from collections import namedtuple
import cv2
import json

from drawables import RandomBall, ChaserBall
from pose import Pose



class Animation():

    objects = [

        RandomBall(100, 100),
        RandomBall(150, 150),
        RandomBall(200, 200),
    ]

    pose = None

    def __init__(self):
        pass

    def add_pose(self, pose):
        self.pose = pose

    def update_pose(self, pose_points):
        if self.pose is not None:
            self.pose.update_joints(pose_points)

    def update(self):
        for obj in self.objects:
            print(obj)
            obj.update()

    def draw(self, frame):
        for obj in self.objects:
            obj.draw(frame)
        
        return frame

    def draw_pose(self, frame):

        for joint in self.pose.joints.values():
            cv2.circle(frame, (joint.x, joint.y), 10, (0,255,0), -1)

        return frame