from collections import namedtuple
import cv2
import json
from pose import Pose
import numpy as np

from pose import Pose
from animation_states import NotChangingState, ChangingState

from elements import (
    MiddlePoint, 
    ChaserTunnel, 
    TunnelMiddleHands, 
    SpinnerMiddleHands, 
    AngledChaserScreen,
    CenteredLines,
    ChaserLine
)

DEBUG = False

def set_animation():

    pose = Pose()
    animation = Animation()
    animation.add_pose(pose)
    
    return animation


class Animation():

    animation_step = 0
    allow_transparency = False
    objects = {}
    pose = None


    def __init__(self, allow_transparency=False, drawing_pose=False, updating_pose=True):
        self.allow_transparency = allow_transparency
        self._state = NotChangingState(self)

        self.drawing_pose = drawing_pose
        self.updating_pose = updating_pose

    def add_pose(self, pose):
        self.pose = pose

    def update_pose(self, pose_points):
        if self.pose is not None and self.updating_pose:
            self.pose.update_joints(pose_points)

    def update_pose_from_json(self, json_path):
        if self.pose is not None:
            self.pose.update_joints_from_json(json_path)

    def update(self):
        for obj in self.objects.values():
            obj.update()

    def draw(self, frame):

        for obj in self.objects.values():
            frame = obj.draw(frame, allow_transparency=self.allow_transparency)

        if self.drawing_pose:
            frame = self.draw_pose(frame)

        self.animation_step += 1

        return frame

    def draw_pose(self, frame):
        for name, joint in self.pose.joints.items():
            if DEBUG:
                print(name, joint.position)
            
            cv2.circle(frame, (int(joint.position[0]), int(joint.position[1])), 10, (255,255,0), -1)

        return frame

    def key_handler(self, key):
        self._state.key_handler(key)

 