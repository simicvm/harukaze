from collections import namedtuple
import os
import json


class Joint():
    x, y = 0, 0

    def __init__(self, name, idx):
        self.name = name
        self.idx = idx

    def update(self, x, y):
        self.x = x
        self.y = y


class Pose():

    force_int = True

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
            print("updating {}".format(joint_name))
            idx = joint.idx
            pose_point = pose_points[idx]
            x, y = pose_point[:2]

            if self.force_int:
                x = int(x)
                y = int(y)

            joint.update(x, y)


def pose_points_from_json(json_path):

    def _split_points(points):
        return [points[x:x+3] for x in range(0, len(points), 3)]

    with open(json_path) as f:
      inference = json.load(f)

    person_inference = inference.get("people", [{}])[0]
    points = person_inference.get("pose_keypoints_2d", [])
    return _split_points(points)


if __name__ == "__main__":
    inference_directory = 'data/pose_output/output'
    inference_files = sorted([os.path.join(inference_directory, f) for f in os.listdir(inference_directory)])

    pose = Pose()

    for json_file in inference_files:
        print(pose)
        pose_points_ = pose_points_from_json(json_file)

        pose.update_joints(pose_points_)

        print("right_hand ", pose.joints["right_hand"])
        print("right_hand_x ", pose.joints["right_hand"].x)

        print(pose_points_[0])


