from elements import (
    MiddlePoint, SpinnerMiddleHands, ChaserScreen, 
    DoubleScreen, AngledChaserScreen, ChaserSpinner,
    TunnelMiddleHands, CenteredLines
)


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
        elif key == ord("3"):
            print("Tunnel state")
            self.animation._state = TunnelState(self.animation)
        elif key == ord("4"):
            print("Cross state")
            self.animation._state = CrossState(self.animation)


        if key == ord("p"):
            self.animation.drawing_pose = not self.animation.drawing_pose
            print("drawing pose: {}".format(self.animation.drawing_pose))

        if key == ord("o"):
            self.animation.updating_pose = not self.animation.updating_pose
            print("drawing pose: {}".format(self.animation.updating_pose))

        if key == ord("["):
            self.animation.drawing_animation = not self.animation.drawing_animation
            print("drawing animation: {}".format(self.animation.drawing_animation))



class SpiralState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_position = self.animation.pose.joints["head"].position
        center_hands = MiddlePoint(point_a=self.animation.pose.joints["left_hand"], 
                                   point_b=self.animation.pose.joints["right_hand"])
        spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands, position=initial_position)

        self.animation.objects = {
            "center_hands": center_hands,
            "spinner_center_hands": spinner_chaser_middle_hands
        }

    def key_handler(self, key):
        if key == ord("r"):
            print("decreasing n_circles")
            if self.animation.objects["spinner_center_hands"].n_circles > 0:
                self.animation.objects["spinner_center_hands"].n_circles -= 1
        elif key == ord("t"):
            print("increasing n_circles")
            self.animation.objects["spinner_center_hands"].n_circles += 1

        elif key == ord("f"):
            print("decreasing min_radius")
            if self.animation.objects["spinner_center_hands"].min_radius > 0:
                self.animation.objects["spinner_center_hands"].min_radius -= 1
        elif key == ord("g"):
            print("increasing min_radius")
            self.animation.objects["spinner_center_hands"].min_radius += 1

        elif key == ord("y"):
            print("change thickness")
            if self.animation.objects["spinner_center_hands"].thickness == -1:
                self.animation.objects["spinner_center_hands"].thickness = 10
            else:
                self.animation.objects["spinner_center_hands"].thickness = -1

        else:
            ChangingState.key_handler(self, key)


class ScreenState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_position = self.animation.pose.joints["head"].position
        chaser_screen = ChaserScreen(chase_to=self.animation.pose.joints["head"], color_a=(0,0,0), color_b=(0,0,190), mode="horizontal")
        self.animation.objects = {
            "chaser_screen": chaser_screen
        }

    def key_handler(self, key):
        ChangingState.key_handler(self, key)


class HandState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation.objects = {}

        self.has_right_hand = False
        self.has_left_hand = False

    def key_handler(self, key):
        ChangingState.key_handler(self, key)
        if key == ord("r"):
            print("adding right hand")
            chaser_right = ChaserSpinner(
                chase_to=self.animation.pose.joints["right_hand"],
                max_speed=15,
                center_radius=5
                )

            self.animation.objects["right_hand"] = chaser_right

        if key == ord("l"):
            print("adding left hand")
            chaser_left = ChaserSpinner(
                chase_to=self.animation.pose.joints["left_hand"],
                max_speed=15,
                center_radius=5)
            self.animation.objects["left_hand"] = chaser_left

        if key == ord("h"):
            print("adding head hand")
            chaser_head = ChaserSpinner(
                chase_to=self.animation.pose.joints["head"],
                max_speed=15,
                center_radius=5)
            self.animation.objects["head"] = chaser_head


class TunnelState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_position = self.animation.pose.joints["head"].position

        center_hands = MiddlePoint(
            point_a=self.animation.pose.joints["right_hand"], 
            point_b=self.animation.pose.joints["left_hand"])
        # spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands, position=initial_position)

        tunnel_chaser_middle_hands = TunnelMiddleHands(position=initial_position, chase_to=center_hands)

        self.animation.objects = {
            "center_hands": center_hands,
            "tunnel": tunnel_chaser_middle_hands
        }
    def key_handler(self, key):
        ChangingState.key_handler(self, key)


class CrossState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initial_position = self.animation.pose.joints["head"].position

        center_hands = MiddlePoint(
            point_a=self.animation.pose.joints["right_hand"], 
            point_b=self.animation.pose.joints["left_hand"])
        # spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands, position=initial_position)

        cross = CenteredLines(

            land_distance=0,
            # position=initial_position, 
            chase_to=center_hands)

        self.animation.objects = {
            "center_hands": center_hands,
            "cross": cross
        }
    def key_handler(self, key):
        ChangingState.key_handler(self, key)