import os
import sys
import json
import time
import argparse
from multiprocessing import Process, Queue, Manager, Pipe

import cv2
import numpy as np
import pyrealsense2 as rs

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
        "--op-process-real-time",
        default=False,
        action="store_true",
        help="Enable to keep the original source frame rate"
    )
    parser.add_argument(
        "--data-path",
        default=None,
        type=str,
        help="Absolute path to the folder containing source video and (optionally) pose files.",
    )
    parser.add_argument(
        "--no-inference",
        default=False,
        action="store_true",
        help="Use to load poses from json and not run live inference."
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


def get_pose_from_openpose(pose_pipe):
    pose_points_old = np.zeros((1, 25, 3), dtype=np.uint8)
    while True:
        if pose_pipe.poll():
            pose_points = pose_pipe.recv()
            if pose_points.ndim != 3:
                pose_points = pose_points_old
        else:
            pose_points = pose_points_old
        pose_points_old = pose_points
        yield pose_points_old, pose_points


def get_pose_from_file(inference_files):
    def _split_points(points):
        return [points[x:x+3] for x in range(0, len(points), 3)]

    for json_path in inference_files:
        with open(json_path) as f:
            inference = json.load(f)
            person_inference = inference.get("people", [{}])[0]
            points = person_inference.get("pose_keypoints_2d", [])
            points = _split_points(points)
            yield None, [points]


def project_visuals(
        video_file=None,
        pose_files=None,
        frame_name="Frame",
        openpose_params=None,
        image_pipe=None,
        pose_pipe=None,
        animation=None,
        calibrator=None,
        no_inference=None
):
    if video_file is None:
        stream, pipe, profile = initialize_realsense(frame_name=frame_name)
        get_image = get_image_from_realsense
        get_pose = get_pose_from_openpose(pose_pipe)

    elif os.path.isfile(video_file):
        cap = cv2.VideoCapture(video_file)
        get_image = lambda x: cap.read()
        pipe = None
        if not no_inference:
            get_pose = get_pose_from_openpose(pose_pipe)
        elif pose_files is not None:
            get_pose = get_pose_from_file(pose_files)

    else:
        return "Error, running mode not specified properly!"

    while True:
        start_time = time.time()
        _, color_image = get_image(pipe)
        # Not sure if this resizing is useful here. On the one hand I moved the resizing
        # from the OP process to the main one. On the other hand there is much less data
        # to be serialized and sent over the pipe.
        # color_image = cv2.resize(color_image, (464, 256), interpolation=cv2.INTER_LINEAR)

        if not no_inference:
            image_pipe.send(color_image)
        pose_points_old, pose_points = next(get_pose)

        black_image = np.zeros((720, 1280, 3), dtype=np.uint8)
        # color_image = black_image

        animation.update_pose(pose_points[0])
        animation.update()
        # color_image = animation.draw(color_image)
        animation.draw_pose(color_image)

        if calibrator.calibrating:
            calibrator.display_calibration(color_image)

        color_image = calibrator.calibrate(color_image)
        cv2.imshow(frame_name, color_image)

        # print(
        #     "FPS: ", 1.0 / (time.time() - start_time)
        # )  # FPS = 1 / time to process loop

        key = cv2.waitKey(1)
        calibrator.key_handler(key)
        if key == ord("q"):
            stream.release()
            cv2.destroyAllWindows()
            return "Closing the app, user pressed 'q' key!"


if __name__ == "__main__":
    if sys.platform == "linux":
        from openpose import pyopenpose as op
    else:
        print("Running without Openpose!")

    arguments = parse_arguments()
    openpose_params = set_openpose(arguments)
    video_file = None
    pose_files = None

    if arguments[0].data_path is not None:
        data_path = arguments[0].data_path
        assert os.path.isdir(data_path), "Data folder does not exist."
        pose_files = sorted([os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith(".json")])
        video_file = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith(".avi")]
        assert len(video_file) == 1, "Data path has to contain only one video!"
        video_file = video_file[0]

    image_pipe_parent, image_pipe_child = Pipe()
    pose_pipe_parent, pose_pipe_child = Pipe()
    if not arguments[0].no_inference:
        p_1 = Process(
            target=run_openpose,
            daemon=True,
            args=(openpose_params, image_pipe_child, pose_pipe_child),
        )
        p_1.start()

    animation = set_animation()
    calibrator = set_calibrator(
        # tl=[-340, -165],
        # tr=[140, -125],
        # br=[95, 50],
        # bl=[-255, 90]
    )
    message = project_visuals(
        video_file=video_file,
        pose_files=pose_files,
        image_pipe=image_pipe_parent,
        pose_pipe=pose_pipe_parent,
        openpose_params=openpose_params,
        animation=animation,
        calibrator=calibrator,
        no_inference=arguments[0].no_inference
    )
    print(message)
    if not arguments[0].no_inference:
        p_1.join()
