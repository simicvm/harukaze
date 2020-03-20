from collections import namedtuple
import cv2
import json
from pose import Pose
import numpy as np

from pose import Pose
from animation_states import NotChangingState

from elements import MiddlePoint, ChaserTunnel, TunnelMiddleHands, SpinnerMiddleHands

DEBUG = False

def set_animation():

    pose = Pose()
    animation = Animation()
    animation.add_pose(pose)

    center_hands = MiddlePoint(point_a=animation.pose.joints["right_hand"], point_b=animation.pose.joints["left_hand"])

    spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands)
    # chaser_screen = ChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0))

    # angled_chaser_screen = AngledChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190), 
    #                                           point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])
    # double_screen = DoubleScreen(point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])

    # tunnel = ChaserTunnel(chase_to=animation.pose.joints["head"])
    # tunnel_chaser_middle_hands = TunnelMiddleHands(chase_to=center_hands, colors=[(0,0,0), (0,190,0)])

    animation.objects.extend([
        center_hands,
        # tunnel_chaser_middle_hands
        # double_screen,
        spinner_chaser_middle_hands,
        # angled_chaser_screen,
    ])
    return animation


class Animation():

    allow_transparency = False

    objects = [
    ]

    pose = None

    def __init__(self, allow_transparency=False):
        self.allow_transparency = allow_transparency
        self._state = NotChangingState(self)

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
        for name, joint in self.pose.joints.items():
            if DEBUG:
                print(name, joint.position)
            
            cv2.circle(frame, (int(joint.position[0]), int(joint.position[1])), 10, (255,255,0), -1)

        return frame

    def key_handler(self, key):
        self._state.key_handler(key)


