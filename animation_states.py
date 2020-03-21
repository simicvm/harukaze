from elements import MiddlePoint, SpinnerMiddleHands, ChaserScreen, DoubleScreen, AngledChaserScreen, ChaserSpinner


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
            print("Hand state")
            self.animation._state = HandState(self.animation)




class SpiralState(ChangingState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_position = self.animation.pose.joints["head"].position
        center_hands = MiddlePoint(
            point_a=self.animation.pose.joints["right_hand"], 
            point_b=self.animation.pose.joints["left_hand"])
        spinner_chaser_middle_hands = SpinnerMiddleHands(chase_to=center_hands, position=initial_position)

        self.animation.objects = {
            "center_hands": center_hands,
            "spinner_center_hands": spinner_chaser_middle_hands
        }

    def key_handler(self, key):
        if key == ord("o"):
            print("decreasing n_circles")
            if self.animation.objects["spinner_center_hands"].n_circles > 0:
                self.animation.objects["spinner_center_hands"].n_circles -= 1
        elif key == ord("p"):
            print("increasing n_circles")
            self.animation.objects["spinner_center_hands"].n_circles += 1

        elif key == ord("l"):
            print("decreasing min_radius")
            if self.animation.objects["spinner_center_hands"].min_radius > 0:
                self.animation.objects["spinner_center_hands"].min_radius -= 1
        elif key == ord(";"):
            print("increasing min_radius")
            self.animation.objects["spinner_center_hands"].min_radius += 1
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
        self.animation.objects = [
        ]

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
