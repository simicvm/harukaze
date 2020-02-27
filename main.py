import os
import sys
import json
import time
import argparse
from multiprocessing import Process, Queue, Manager, Pipe

import cv2
import numpy as np
import pyrealsense2 as rs
from openpose import pyopenpose as op

from animation import set_animation
from calibrator import set_calibrator


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
        "--op-output-resolution",
        default="-1x-1",
        type=str,
        help="The image resolution to output and scale results to"
    )
    parser.add_argument(
        "--op-keypoint-scale",
        default=0,
        type=int,
        help="Scaling to the output coordinates."
    )
    parser.add_argument(
        "--otput-pose-dir",
        default="~/harukaze/output",
        type=str,
        help="Absolute path to the desired output folder.",
    )
    parser.add_argument(
        "--data-path",
        default=None,
        type=str,
        help="Absolute path to the folder containing source video and (optionally) pose files.",
    )
    return parser.parse_known_args()


def set_openpose(args):
    params = dict()

    for arg in vars(args[0]):
        if arg.startswith("op_"):
            val = getattr(args[0], arg)
            if val is not None:
                argument = arg.replace("op_", "")
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


def get_pose_from_openpose(pose_pipe, _):
    if pose_pipe.poll():
        pose_points = pose_pipe.recv()
        pose_points_old = pose_points
    else:
        pose_points = pose_points_old
    return pose_points_old, pose_points


def get_pose_from_file(_, i):
    json_path = inference_files[i]
    animation.update_pose_from_json(json_path)
    return None


def project_visuals(
        video_file=None,
        pose_files=None,
        frame_name="Frame",
        openpose_params=None,
        image_pipe=None,
        pose_pipe=None,
        animation=None
):
    if video_file is None:
        stream, pipe, profile = initialize_realsense(frame_name=frame_name)
        get_image = get_image_from_realsense
        get_pose = get_pose_from_openpose

    elif os.path.isfile(video_file):
        cap = cv2.VideoCapture(video_file)
        get_image = lambda x: cap.read()
        pipe = None
        if pose_files is not None:
            get_pose = get_pose_from_file

    else:
        return "Error, running mode not specified properly!"

    # datum, opWrapper = initialize_openpose(openpose_params)
    pose_points_old = np.zeros((720, 1280, 3), dtype=np.uint8)

    i = 0
    while True:
        start_time = time.time()
        _, color_image = get_image(pipe)
        # Not sure if this resizing is useful here. On the one hand I moved the resizing
        # from the OP process to the main one. On the other hand there is much less data
        # to be serialized and sent over the pipe.
        color_image = cv2.resize(color_image, (464, 256), interpolation=cv2.INTER_LINEAR)

        image_pipe.send(color_image)
        pose_points_old, pose_points = get_pose(pose_pipe, i)

        # datum.cvInputData = color_image
        # opWrapper.emplaceAndPop([datum])
        # pose_points = datum.poseKeypoints
        black_image = np.zeros((720, 1280, 3), dtype=np.uint8)

        animation.update_pose(pose_points)
        # animation.draw_pose(color_image)
        color_image = animation.draw(color_image)

        cv2.imshow(frame_name, color_image)

        print(
            "FPS: ", 1.0 / (time.time() - start_time)
        )  # FPS = 1 / time to process loop

        i += 1
        key = cv2.waitKey(1)
        if key == ord("q"):
            stream.release()
            cv2.destroyAllWindows()
            return "Closing the app, user pressed 'q' key!"


if __name__ == "__main__":
    arguments = parse_arguments()
    openpose_params = set_openpose(arguments)

    if arguments.data_path is not None:
        data_path = arguments.data_path
        assert os.path.isdir(data_path), "Data folder does not exist."
        pose_files = sorted([f for f in os.listdir(data_path) if f.endswith(".json")])
        video_file = [f for f in os.listdir(data_path) if f.endswith(".avi")]
        assert len(video_file) == 1, "Data path has to contain only one video!"

    image_pipe_parent, image_pipe_child = Pipe()
    pose_pipe_parent, pose_pipe_child = Pipe()
    p_1 = Process(
        target=run_openpose,
        daemon=True,
        args=(openpose_params, image_pipe_child, pose_pipe_child),
    )
    p_1.start()

    animation = set_animation()
    message = project_visuals(
        video_file=video_file[0],
        pose_files=pose_files,
        image_pipe=image_pipe_parent,
        pose_pipe=pose_pipe_parent,
        openpose_params=openpose_params,
        animation=animation
    )
    print(message)
    p_1.join()
