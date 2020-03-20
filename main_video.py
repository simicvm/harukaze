import os
import sys
import json
import time
import argparse
from multiprocessing import Process, Queue, Manager, Pipe

import cv2
import numpy as np
import pyrealsense2 as rs
# from openpose import pyopenpose as op

from animation import set_animation
from calibrator import set_calibrator

START_FROM_FRAME = 0

def parse_arguments():
    parser = argparse.ArgumentParser(description="Harukaze performance code.")
    parser.add_argument(
        "--op-model-folder",
        default="~/openpose/models/",
        type=str,
        help="Absolute path to network models.",
    )
    parser.add_argument(
        "--otput-pose-dir",
        default="~/harukaze/output",
        type=str,
        help="Absolute path to the desired output folder.",
    )
    parser.add_argument(
        "--data-dir",
        default="~/harukaze/data",
        type=str,
        help="Absolute path to the folder containing data for inference.",
    )
    return parser.parse_known_args()


def set_openpose(args):
    params = dict()
    # manager = Manager()
    # params = manager.dict()

    for arg in vars(args[0]):
        if arg.startswith("op_"):
            val = getattr(args[0], arg)
            argument = arg.strip("op_")
            params[argument] = val
    # print(params)
    return params


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


def initialize_realsense(frame_name):
    cv2.namedWindow(frame_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        frame_name,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )
    stream = cv2.VideoCapture(-1)
    pipe = rs.pipeline()
    profile = pipe.start()
    return stream, pipe, profile


def project_visuals(
        run_live=False,
        data_file=None,
        frame_name="Frame",
        image_pipe=None,
        pose_pipe=None
    ):

    # TODO: remove at handling videos on main
    
    inference_directory = '../data/ai_office_dance'
    inference_files = sorted([os.path.join(inference_directory, f) for f in os.listdir(inference_directory)])
    data_file = '../data/ai_office_dance.avi'

    animation = set_animation()
    calibrator = set_calibrator()

    print(data_file)

    cap = cv2.VideoCapture(data_file)

    i = -1
    while True:
        i += 1
        
        start_time = time.time()
        ret, color_image = cap.read()

        if i < START_FROM_FRAME:
            continue
        else:
            time.sleep(0.001)
        

        # print("FRAME {}".format(i))
        json_path = inference_files[i]

        animation.update_pose_from_json(json_path)

        animation.draw(color_image)
        animation.update()

        animation.draw_pose(color_image)

        if calibrator.calibrating:
            calibrator.display_calibration(color_image)

        color_image = calibrator.calibrate(color_image)

        cv2.imshow(frame_name, color_image)

        key = cv2.waitKey(1)
        if key == ord("q"):
            cv2.destroyAllWindows()
            print("Closing the app, user pressed 'q' key!")
            return

        calibrator.key_handler(key)
        animation.key_handler(key)


if __name__ == "__main__":

    project_visuals()
