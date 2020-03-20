import numpy as np
import cv2

tl = None
tr = None
br = None
bl = None


def set_calibrator(tl=tl, tr=tr, br=br, bl=bl):
    return Calibrator(tl=tl, tr=tr, br=br, bl=bl)


# class CalibratorState():


class Calibrator():

    unit = 5

    calibrating = False
    calibrating_tl = False
    calibrating_tr = False
    calibrating_br = False
    calibrating_bl = False

    def __init__(self, tl=None, tr=None, br=None, bl=None):
        self.tl = tl if tl is not None else [0, 0]
        self.tr = tr if tr is not None else [0, 0]
        self.bl = bl if bl is not None else [0, 0]
        self.br = br if br is not None else [0, 0]

        self.calibration = [self.tl, self.tr, self.br, self.bl]

    @staticmethod
    def draw_calibration_frame(image, n_frames=10):

        color = (0,0,255)
        thickness = 2
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
                    self.tl[0], self.tl[1], self.tr[0], self.tr[1], self.br[0], self.br[1], self.bl[0], self.bl[1]), 
                    (int(width/4), int(height/2+30)), 2, 1, (0, 255, 255))

    def calibrate(self, image):

        if sum(np.array(self.calibration).reshape(-1)) == 0:
            return image

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





