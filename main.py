import os
import sys
import json
import time
import argparse
from multiprocessing import Process, Queue, Manager, Pipe

import cv2
import numpy as np
import pyrealsense2 as rs

from pose import Pose, pose_points_from_json
from animation import Animation
from drawables import SpinningChaserBall, SpinningFixedBall, SpinningRandomBall, ChaserSpinningMiddleHands

if sys.platform == "linux":
    from openpose import pyopenpose as op
elif sys.platform == "darwin":
    print("Running without OpenPose module.")
else:
    print("Platform not recognized. Terminating!")
    sys.exit()

pose = Pose()
animation = Animation()
animation.add_pose(pose)


animation.objects.append(
    ChaserSpinningMiddleHands(name="ball_1", right_hand=pose.joints["right_hand"], left_hand=pose.joints["left_hand"], x=300, y=300)
)
# animation.objects.append(
#     SpinningChaserBall(name="ball_1", chase_to=pose.joints["right_hand"], x=300, y=300)
# )
# animation.objects.append(
#     SpinningChaserBall(name="ball_2", chase_to=pose.joints["left_hand"], x=300, y=300)
# )
# animation.objects.append(SpinningChaserBall(name="ball_3", chase_to=pose.joints["head"], x=300, y=300))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Harukaze performance code.")
    parser.add_argument(
        "--op-model-folder",
        default="~/openpose/models/",
        type=str,
        help="Absolute path to network models.",
    )
    parser.add_argument(
        "--op-tracking",
        type=int,
        help="Number of frames to track."
    )
    parser.add_argument(
        "--op-number-people-max",
        default=1,
        type=int,
        help="Number of people to estimate pose."
    )
    parser.add_argument(
        "--op-render-pose",
        default=1,
        type=int,
        help="Render pose on CPU, GPU, or don't."
    )
    parser.add_argument(
        "--op-net_resolution",
        default="-1x368",
        type=str,
        help="Input resolution to the network. Multiples of 16."
    )
    parser.add_argument(
        "--op-disable-multi-thread",
        default=False,
        action="store_true",
        help="Enable for lower latency."
    )
    parser.add_argument(
        "--otput-pose-dir",
        default="~/harukaze/output",
        type=str,
        help="Absolute path to the desired output folder.",
    )
    parser.add_argument(
        "--data-file",
        default=None,
        type=str,
        help="Absolute path to the video file.",
    )
    return parser.parse_known_args()


def set_openpose(args):
    params = dict()

    for arg in vars(args[0]):
        if arg.startswith("op_"):
            val = getattr(args[0], arg)
            if val is not None:
                argument = arg.strip("op_")
                params[argument] = val
    return params


def initialize_openpose(openpose_params):
    print(openpose_params)
    opWrapper = op.WrapperPython()
    opWrapper.configure(openpose_params)
    opWrapper.start()

    datum = op.Datum()
    print("Initialized OpenPose!")

    return datum, opWrapper


def run_openpose(openpose_params, image_pipe, pose_pipe):
    print(openpose_params)
    opWrapper = op.WrapperPython()
    opWrapper.configure(openpose_params)
    opWrapper.start()

    datum = op.Datum()
    print("Initialized OpenPose!")

    while True:
        image = image_pipe.recv()
        datum.cvInputData = image
        opWrapper.emplaceAndPop([datum])
        pose_pipe.send(datum.poseKeypoints)


def initialize_realsense(frame_name="Frame", res_w=1280, res_h=720, fps=30):
    cv2.namedWindow(frame_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        frame_name,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )
    stream = cv2.VideoCapture(-1)
    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, res_w, res_h, rs.format.rgb8, fps)
    profile = pipe.start(config)
    return stream, pipe, profile


def get_image_from_realsense(pipe):
    frames = pipe.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())
    color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
    return None, color_image


def project_visuals(
        data_file=None,
        frame_name="Frame",
        openpose_params=None,
        image_pipe=None,
        pose_pipe=None,
):
    if data_file is None:
        stream, pipe, profile = initialize_realsense(frame_name=frame_name)
        get_image = get_image_from_realsense
    elif os.path.isfile(data_file):
        cap = cv2.VideoCapture(data_file)
        get_image = lambda x: cap.read()
        pipe = None
    else:
        return "Error, running mode not specified properly!"

    # datum, opWrapper = initialize_openpose(openpose_params)
    pose_points_old = np.zeros((720, 1280, 3), dtype=np.uint8)
    while True:
        start_time = time.time()
        _, color_image = get_image(pipe)

        image_pipe.send(color_image)
        if pose_pipe.poll():
            pose_points = pose_pipe.recv()
            pose_points_old = pose_points
        else:
            pose_points = pose_points_old

        # datum.cvInputData = color_image
        # opWrapper.emplaceAndPop([datum])
        # pose_points = datum.poseKeypoints
        black_image = np.zeros((720, 1280, 3), dtype=np.uint8)

        if pose_points.ndim != 3:
            continue
        pose_points = pose_points[0]
        if len(pose_points) == 25:
            animation.update_pose(pose_points)
        # animation.draw_pose(color_image)
        # animation.draw_pose(black_image)
        animation.update()
        # color_image = animation.draw(color_image)
        color_image = animation.draw(black_image)

        cv2.imshow(frame_name, color_image)

        print(
            "FPS: ", 1.0 / (time.time() - start_time)
        )  # FPS = 1 / time to process loop

        key = cv2.waitKey(1)
        if key == ord("q"):
            stream.release()
            cv2.destroyAllWindows()
            return "Closing the app, user pressed 'q' key!"


if __name__ == "__main__":
    arguments = parse_arguments()
    openpose_params = set_openpose(arguments)
    image_pipe_parent, image_pipe_child = Pipe()
    pose_pipe_parent, pose_pipe_child = Pipe()
    p_1 = Process(
        target=run_openpose,
        daemon=True,
        args=(openpose_params, image_pipe_child, pose_pipe_child),
    )
    p_1.start()
    message = project_visuals(
        data_file=arguments[0].data_file,
        image_pipe=image_pipe_parent,
        pose_pipe=pose_pipe_parent,
        openpose_params=openpose_params
    )
    print(message)
    # p_1.join()
