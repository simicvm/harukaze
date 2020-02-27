from collections import namedtuple
import cv2
import json
from pose import Pose
import numpy as np

from pose import Pose
from drawables import ChaserSpinningMiddleHands


def set_animation():

    pose = Pose()
    animation = Animation()
    animation.add_pose(pose)

    animation.objects.append(
        ChaserSpinningMiddleHands(
            name="ball_1", 
            right_hand=pose.joints["right_hand"], 
            left_hand=pose.joints["left_hand"], 
            position=np.array([500,500])
        )
    )
    return animation


class Animation():

    allow_transparency = False

    objects = [
    ]

    pose = None

    def __init__(self, allow_transparency=False):
        self.allow_transparency = allow_transparency

    def add_pose(self, pose):
        self.pose = pose

    def update_pose(self, pose_points):
        if self.pose is not None:
            self.pose.update_joints(pose_points)

    def update_pose_from_json(self, json_path):
        if self.pose is not None:
            self.pose.update_joints_from_json(json_path)

    def update(self):
        for obj in self.objects:
            obj.update()

    def draw(self, frame):
        for obj in self.objects:
            frame = obj.draw(frame, allow_transparency=self.allow_transparency)

        return frame

    def draw_pose(self, frame):
        for joint in self.pose.joints.values():
            cv2.circle(frame, (int(joint.position[0]), int(joint.position[1])), 10, (0,255,0), -1)

        return frame
