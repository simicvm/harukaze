import numpy as np
import cv2

tl = None
tr = None
br = None
bl = None


def set_calibrator(tl=tl, tr=tr, br=br, bl=bl, *args, **kwargs):
    return Calibrator(tl=tl, tr=tr, br=br, bl=bl, *args, **kwargs)


# class CalibratorState():


class Calibrator():

    calibrating = False
    calibrating_tl = False
    calibrating_tr = False
    calibrating_br = False
    calibrating_bl = False

    def __init__(self, tl=None, tr=None, br=None, bl=None, unit=5, aspect_ratio=1.78, angle=0):
        self.tl = tl if tl is not None else [0, 0]
        self.tr = tr if tr is not None else [0, 0]
        self.bl = bl if bl is not None else [0, 0]
        self.br = br if br is not None else [0, 0]

        self.calibration = [self.tl, self.tr, self.br, self.bl]

        self.unit = unit

        self.aspect_ratio = aspect_ratio

        self.angle = angle


    @staticmethod
    def draw_calibration_frame(image, n_frames=10):

        color = (0,0,255)
        thickness = 1
        height, width = image.shape[:2]

        for offset in np.linspace(5, max(height, width), n_frames):
            cv2.line(image, (int(offset), 0), (int(offset), int(height)), color, thickness)
            cv2.line(image, (0, int(offset)), (int(width), int(offset)), color, thickness)

        cv2.line(image, (0, 0), (int(width), int(height)), color, thickness)
        cv2.line(image, (int(width), 0), (0, int(height)), color, thickness)

    
    def display_calibration(self, image):
        
        height, width = image.shape[:2]

        if self.calibrating_tl:
            cv2.putText(image, "[1] TOP LEFT", (int(width/4), int(height/2 - 50)), 4, 2, (0, 0, 255))
        if self.calibrating_tr:
            cv2.putText(image, "[2] TOP RIGHT", (int(width/4), int(height/2 - 50)), 4, 2, (0, 0, 255))
        if self.calibrating_br:
            cv2.putText(image, "[3] BOTTOM RIGHT", (int(width/4), int(height/2 - 50)), 4, 2, (0, 0, 255))
        if self.calibrating_bl:
            cv2.putText(image, "[4] BOTTOM LEFT", (int(width/4), int(height/2 - 50)), 4, 2, (0, 0, 255))

        self.draw_calibration_frame(image)

        cv2.putText(image, "PERSPECTIVE calibration", (int(width/4), int(height/2)), 4, 2, (0, 0, 255))
        cv2.putText(image, "[[{}, {}], [{}, {}], [{}, {}], [{}, {}]]".format(
                    round(self.tl[0], 2), round(self.tl[1], 2), 
                    round(self.tr[0], 2), round(self.tr[1], 2), 
                    round(self.br[0], 2), round(self.br[1], 2), 
                    round(self.bl[0], 2), round(self.bl[1], 2)), 
                    (int(width/4), int(height/2+30)), 2, 1, (0, 255, 255))

        cv2.putText(image, "ANGLE: {}".format(self.angle), 
                    (int(width/4), int(height/2+30)+100), 2, 1, (0, 255, 255))

    def calibrate(self, image):

        # if sum(np.array(self.calibration).reshape(-1)) == 0:
        #     return image

        height, width = image.shape[:2]
        size = (width, height)

        rect = np.array([[0, 0], [width, 0], [width, height], [0, height]], np.float32)
        dst = np.array([
            rect[0] + self.tl,
            rect[1] + self.tr,
            rect[2] + self.br,
            rect[3] + self.bl
        ], np.float32)

        M = cv2.getPerspectiveTransform(rect, dst)
        image = cv2.warpPerspective(image, M, size)

        rot_center = (width/2, height/2)
        angle = self.angle
        rotation_matrix = cv2.getRotationMatrix2D(rot_center, angle, 1)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
        image = rotated_image

        return image

    def key_handler(self, key):

        if self.calibrating:
            if key == ord("c"):
                print("finish calibration: {}".format(self.calibration))
                self.calibrating_tl = False
                self.calibrating_tr = False
                self.calibrating_br = False
                self.calibrating_bl = False
                self.calibrating = False
            
            # move all 
            if key == 0: # up
                self.tl[1] -= self.unit
                self.tr[1] -= self.unit
                self.bl[1] -= self.unit
                self.br[1] -= self.unit
            elif key == 1: #down
                self.tl[1] += self.unit
                self.tr[1] += self.unit
                self.bl[1] += self.unit
                self.br[1] += self.unit
            elif key == 2: #left
                self.tl[0] -= self.unit
                self.tr[0] -= self.unit
                self.bl[0] -= self.unit
                self.br[0] -= self.unit
            elif key == 3: #right
                self.tl[0] += self.unit
                self.tr[0] += self.unit
                self.bl[0] += self.unit
                self.br[0] += self.unit

            # expand
            if key == ord("z"): 
                self.tl[0] -= round(self.unit * self.aspect_ratio, 2)
                self.tl[1] -= self.unit

                self.tr[0] += round(self.unit * self.aspect_ratio, 2)
                self.tr[1] -= self.unit

                self.bl[0] -= round(self.unit * self.aspect_ratio, 2)
                self.bl[1] += self.unit

                self.br[0] += round(self.unit * self.aspect_ratio, 2)
                self.br[1] += self.unit

            # contract
            elif key == ord("x"): 
                self.tl[0] += round(self.unit * self.aspect_ratio, 2)
                self.tl[1] += self.unit

                self.tr[0] -= round(self.unit * self.aspect_ratio, 2)
                self.tr[1] += self.unit

                self.bl[0] += round(self.unit * self.aspect_ratio, 2)
                self.bl[1] -= self.unit

                self.br[0] -= round(self.unit * self.aspect_ratio, 2)
                self.br[1] -= self.unit

            # rotate left
            if key == ord("e"): 
                print("rotating left")
                self.angle -= self.unit
            elif key == ord("r"): 
                print("rotating right")
                self.angle += self.unit

            # TOP LEFT CORNER
            if self.calibrating_tl:
                if key == ord("w"):
                    self.tl[1] -= self.unit # move up
                elif key == ord("s"):
                    self.tl[1] += self.unit # move down
                elif key == ord("a"):
                    self.tl[0] -= self.unit # move left
                elif key == ord("d"):
                    self.tl[0] += self.unit # move right

            if key == ord("1") and not self.calibrating_tl:
                self.calibrating_tl = True
                self.calibrating_tr = False
                self.calibrating_br = False
                self.calibrating_bl = False
            elif key == ord("1") and self.calibrating_tl:
                self.calibrating_tl = False 

            
            # TOP RIGHT CORNER
            if self.calibrating_tr:
                if key == ord("w"):
                    self.tr[1] -= self.unit # move up
                elif key == ord("s"):
                    self.tr[1] += self.unit # move down
                elif key == ord("a"):
                    self.tr[0] -= self.unit # move left
                elif key == ord("d"):
                    self.tr[0] += self.unit # move right

            if key == ord("2") and not self.calibrating_tr:
                self.calibrating_tl = False
                self.calibrating_tr = True
                self.calibrating_br = False
                self.calibrating_bl = False
            elif key == ord("2") and self.calibrating_tr:
                self.calibrating_tr = False 
            

            # BOTTOM RIGHT CORNER
            if self.calibrating_br:
                if key == ord("w"):
                    self.br[1] -= self.unit # move up
                elif key == ord("s"):
                    self.br[1] += self.unit # move down
                elif key == ord("a"):
                    self.br[0] -= self.unit # move left
                elif key == ord("d"):
                    self.br[0] += self.unit # move right

            if key == ord("3") and not self.calibrating_br:
                self.calibrating_tl = False
                self.calibrating_tr = False
                self.calibrating_br = True
                self.calibrating_bl = False
            elif key == ord("3") and self.calibrating_br:
                self.calibrating_br = False 


            # BOTTOM LEFT CORNER
            if self.calibrating_bl:
                if key == ord("w"):
                    self.bl[1] -= self.unit # move up
                elif key == ord("s"):
                    self.bl[1] += self.unit # move down
                elif key == ord("a"):
                    self.bl[0] -= self.unit # move left
                elif key == ord("d"):
                    self.bl[0] += self.unit # move right

            if key == ord("4") and not self.calibrating_bl:
                self.calibrating_tl = False
                self.calibrating_tr = False
                self.calibrating_br = False
                self.calibrating_bl = True
            elif key == ord("4") and self.calibrating_bl:
                self.calibrating_bl = False

        else:
            if key == ord("c"):
                print("start calibration")
                self.calibrating = True





