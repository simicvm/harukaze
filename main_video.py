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

from pose import Pose, pose_points_from_json
from animation import Animation
from drawables import ChaserSpinningMiddleHands


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
    # fan_graphics = cv2.imread("/home/ascent/Pictures/fan_diff_small.png")
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

    print(data_file)

    cap = cv2.VideoCapture(data_file)

    i = 0
    while True:
        start_time = time.time()

        ret, color_image = cap.read()
        width, height = color_image.shape[:2]
        
        json_path = inference_files[i]
        pose_points = pose_points_from_json(json_path)

        if len(pose_points) == 25:
            animation.update_pose(pose_points)

        animation.draw_pose(color_image)
        animation.update()
        color_image = animation.draw(color_image)

        cv2.imshow(frame_name, color_image)

        print(
            "FPS: ", 1.0 / (time.time() - start_time)
        )  # FPS = 1 / time to process loop

        key = cv2.waitKey(1)
        if key == ord("q"):
            stream.release()
            cv2.destroyAllWindows()
            return "Closing the app, user pressed 'q' key!"

        i += 1
        time.sleep(0.005)

if __name__ == "__main__":
    # arguments = parse_arguments()
    # openpose_params = set_openpose(arguments)
    # q = Queue()
    # image_pipe_send, image_pipe_receive = Pipe()
    # pose_pipe_send, pose_pipe_receive = Pipe()
    # p_1 = Process(
    #     target=run_openpose,
    #     daemon=True,
    #     args=(openpose_params, image_pipe_receive, pose_pipe_send),
    # )
    # p_1.start()
    # message = project_visuals(
    #     run_live=True, image_pipe=image_pipe_send, pose_pipe=pose_pipe_receive
    # )
    # print(message)
    # p_1.join()

    project_visuals()
