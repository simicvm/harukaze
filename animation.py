from collections import namedtuple
import cv2
import json
from pose import Pose
import numpy as np

from pose import Pose
<<<<<<< HEAD
from animation_states import NotChangingState

from elements import MiddlePoint, ChaserTunnel, TunnelMiddleHands, SpinnerMiddleHands
=======
from elements import MiddlePoint, SpinnerMiddleHands, ChaserScreen, DoubleScreen, AngledChaserScreen
>>>>>>> 17e2bf30b355f084eca2e59a345cf43ac6bda004

DEBUG = False

# center_hands = MiddlePoint(point_a=animation.pose.joints["right_hand"], point_b=animation.pose.joints["left_hand"])

# spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands)
# chaser_screen = ChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0))

# angled_chaser_screen = AngledChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190), 
#                                             point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])
# double_screen = DoubleScreen(point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])



def set_animation():

    pose = Pose()
    animation = Animation()
    animation.add_pose(pose)

    center_hands = MiddlePoint(point_a=animation.pose.joints["right_hand"], point_b=animation.pose.joints["left_hand"])

    spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands)
<<<<<<< HEAD
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
=======
    chaser_screen = ChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0))

    angled_chaser_screen = AngledChaserScreen(chase_to=animation.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190), 
                                              point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])
    double_screen = DoubleScreen(point_a=animation.pose.joints["left_hand"], point_b=animation.pose.joints["right_hand"])

    animation.objects.extend([
        center_hands,

        # double_screen,
        # spinner_chaser_middle_hands,
>>>>>>> 17e2bf30b355f084eca2e59a345cf43ac6bda004
        # angled_chaser_screen,
    ])
    return animation


class AnimationState:
    def __init__(self, animation):
        self.animation = animation

    def key_handler(self, key):
        raise NotImplementedError


class NotChangingState(AnimationState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def key_handler(self, key):
        if key == ord("s"):
            print("start changing state")
            self.animation._state = ChangingState(self.animation)


class ChangingState(AnimationState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def key_handler(self, key):
        if key == ord("s"):
            print("stop changing state")
            self.animation._state = NotChangingState(self.animation)
        elif key == ord("1"):
            print("Spiral state")
            self.animation._state = SpiralState(self.animation)
        elif key == ord("2"):
            print("Screen state")
            self.animation._state = ScreenState(self.animation)


class SpiralState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_position = self.animation.pose.joints["head"].position
        center_hands = MiddlePoint(
            point_a=self.animation.pose.joints["right_hand"], 
            point_b=self.animation.pose.joints["left_hand"])
        spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands, position=initial_position)

        self.animation.objects = [
            center_hands,
            spinner_chaser_middle_hands
        ]

    def key_handler(self, key):
        ChangingState.key_handler(self, key)


class ScreenState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_position = self.animation.pose.joints["head"].position
        chaser_screen = ChaserScreen(chase_to=self.animation.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190))
        self.animation.objects = [
            chaser_screen
        ]

    def key_handler(self, key):
        ChangingState.key_handler(self, key)



class Animation():

    allow_transparency = False

    objects = [
    ]

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

<<<<<<< HEAD
=======
    # def key_handler(self, key):

    #     self._state.key_handler(key)

    #     if self.changing_state:

    #         if key == ord("s"):
    #             print("finish changing state")
    #             self.changing_state = False
            
    #         if key == ord("3"):
    #             print("Set to state 1")
    #             initial_position = self.pose.joints["head"].position
    #             center_hands = MiddlePoint(
    #                 point_a=self.pose.joints["right_hand"], 
    #                 point_b=self.pose.joints["left_hand"])
    #             spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands, position=initial_position)

    #             self.objects = [
    #                 center_hands,
    #                 spinner_chaser_middle_hands
    #             ]

    #         if key == ord("4"):
    #             print("Set to state 2")
    #             initial_position = self.pose.joints["head"].position
    #             chaser_screen = ChaserScreen(chase_to=self.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190))
    #             self.objects = [
    #                 chaser_screen
    #             ]
    #     else:
    #         if key == ord("s"):
    #             print("stop changing state")
    #             self.changing_state = True
    #             # import time; time.sleep(5)

>>>>>>> 17e2bf30b355f084eca2e59a345cf43ac6bda004

