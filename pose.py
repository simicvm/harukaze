from collections import namedtuple
import os
import json
import numpy as np

import time

class Joint():

    position = np.array([0, 0])
    previous_position = np.array([0, 0])

    position_delta = position - previous_position
    position_delta_norm = np.linalg.norm(position_delta)

    sensitivity = 20
    max_skips = 3
    skip_n = 0

    def __init__(self, name, idx):
        self.name = name
        self.idx = idx

    def update(self, position):

        if sum(position) > 0:

            position_delta = position - self.position
            position_delta_norm = np.linalg.norm(position_delta)

            print("previous_position_delta: {}".format(position_delta_norm))

            if position_delta_norm < self.sensitivity or self.skip_n == self.max_skips:
                self.previous_position = self.position
                self.position = position
                self.position_delta = position_delta
                self.position_delta_norm = position_delta_norm
                self.skip_n = 0
            else:
                print("skipping: {}".format(self.name))
                self.skip_n += 1
            # else:
            #     exit()
        
        # print(self.position, self.previous_position, self.position_delta, self.position_delta)
        # time.sleep(0.1)


class Pose():

    # force_int = True

    joints = {
        "right_hand": Joint("right_hand", 7),
        "right_elbow": Joint("right_elbow", 6),
        "left_hand": Joint("left_hand", 4),
        "left_elbow": Joint("left_elbow", 3),
        "head": Joint("head", 0),
    }

    def __init__(self):
        pass

    def update_joints(self, pose_points):

        for joint_name, joint in self.joints.items():
            # print("updating {}".format(joint_name))
            idx = joint.idx
            pose_point = pose_points[idx]
            # x, y = pose_point[:2]

            position = np.array(pose_point[:2])

            # if self.force_int:

                # x = int(x)
                # y = int(y)

            joint.update(position)

        


def pose_points_from_json(json_path):

    def _split_points(points):
        return [points[x:x+3] for x in range(0, len(points), 3)]

    with open(json_path) as f:
      inference = json.load(f)

    person_inference = inference.get("people", [{}])[0]
    points = person_inference.get("pose_keypoints_2d", [])
    return _split_points(points)


if __name__ == "__main__":

    inference_directory = '../data/pose_output/output'
    inference_files = sorted([os.path.join(inference_directory, f) for f in os.listdir(inference_directory)])

    pose = Pose()

    for json_file in inference_files:
        # print(pose)
        pose_points_ = pose_points_from_json(json_file)

        pose.update_joints(pose_points_)

        print("right_hand ", pose.joints["right_hand"])
        print("right_hand_x ", pose.joints["right_hand"].x)

        print(pose_points_[0])
