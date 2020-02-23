# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse

import numpy as np
import pyrealsense2 as rs

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../../models/"
    params["no_display"] = True

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    # imageToProcess = cv2.imread(args[0].image_path)
    # datum.cvInputData = imageToProcess
    # opWrapper.emplaceAndPop([datum])

    cv2.namedWindow("projection", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("projection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    fan_graphics = cv2.imread("/home/ascent/Pictures/fan_diff_small.png")
    stream = cv2.VideoCapture(-1)
    pipe = rs.pipeline()
    profile = pipe.start()

    while True:
        # ret, img = stream.read()
        frames = pipe.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

        # Output keypoints and the image with the human skeleton blended on it
        datum.cvInputData = color_image
        opWrapper.emplaceAndPop([datum])

        # Display Image
        # print("Body keypoints: \n" + str(datum.poseKeypoints))
        # import ipdb; ipdb.set_trace()
        # print(f"Neck: {datum.poseKeypoints[:,1,:]}\nRight Wrist: {datum.poseKeypoints[:,4,:]}\nLeft Wrist: {datum.poseKeypoints[:,7,:]}")
        # left_wrist_coord = tuple(datum.poseKeypoints[:,7,:2].squeeze())
        # left_wrist_coord = tuple(datum.poseKeypoints[0][7][:2].squeeze())
        # if left_wrist_coord.dim
        background = np.zeros([720, 1280, 3], dtype=np.uint8)
        # image = cv2.circle(background, center=left_wrist_coord, radius=20, color=(0, 0, 255), thickness=4)
        cv2.imshow("projection", datum.cvOutputData)
        # cv2.imshow("OpenPose 1.5.1 - Tutorial Python API", image)

        key = cv2.waitKey(1)

        if key==ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()
except Exception as e:
    print(e)
    sys.exit(-1)
