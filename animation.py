from collections import namedtuple
import cv2
import json
from pose import Pose
import numpy as np

from pose import Pose
from animation_states import NotChangingState

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

    center_hands = MiddlePoint(point_a=animation.pose.joints["right_hand"], point_b=animation.pose.joints["left_hand"])

    # centered_lines = CenteredLines(chase_to=center_hands)
    # centered_lines = ChaserLine(chase_to=center_hands)

    # spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands)

    # angled_chaser_screen = AngledChaserScreen(
    #     chase_to=animation.pose.joints["head"],
    #     point_a=animation.pose.joints["right_hand"], 
    #     point_b=animation.pose.joints["left_hand"]
    # )
    # chaser_screen = ChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0))

    # angled_chaser_screen = AngledChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190), 
    #                                           point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])
    # double_screen = DoubleScreen(point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])

    # tunnel = ChaserTunnel(chase_to=animation.pose.joints["head"])
    tunnel_chaser_middle_hands = TunnelMiddleHands(chase_to=center_hands)

    animation.objects["center_hands"] = center_hands
    # animation.objects["spinner_center_hands"] = spinner_chaser_middle_hands
    # animation.objects["centered_lines"] = centered_lines
    animation.objects["tunnel"] = tunnel_chaser_middle_hands
    # animation.objects["angled_screen"] = angled_chaser_screen
    
    return animation


class Animation():

    animation_step = 0

    allow_transparency = False

    objects = {
    }

    pose = None
    # changing_state = False


    # self._state = None

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
        for obj in self.objects.values():
            print(obj)
            obj.update()

    def draw(self, frame):
        for obj in self.objects.values():
            frame = obj.draw(frame, allow_transparency=self.allow_transparency)

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

 