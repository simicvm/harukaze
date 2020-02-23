import cv2
import random
from pose import Joint

class Drawable():

    name = ""

    def __init__(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass


class RandomBall(Drawable):
    
    def __init__(self, x, y, name="Ball"):
        self.x = x
        self.y = y
        self.name = name
    
    def draw(self, frame):
        cv2.circle(frame, (self.x, self.y), 10, (150,150,0), -1)

    def update(self):
        self.x += random.choice(range(-10, 10))
        self.y += random.choice(range(-10, 10))


class ChaserBall():

    def __init__(self, chase_to, name="Ball", x=None, y=None):
        
        self.name = name
        self.chase_to = chase_to

        if x is None:
            self.x = self.chase_to.x
        else:
            self.x = x

        if y is None:
            self.y = self.chase_to.y
        else:
            self.y = y
    
    def draw(self, frame):
        cv2.circle(frame, (self.x, self.y), 10, (150,150,0), -1)
        # cv2.line(frame, (self.x, self.y), (self.chase_to.x, self.chase_to.y), (150,150,0), 5)

    def update(self):
        self.x += int((self.chase_to.x - self.x)/10)
        self.y += int((self.chase_to.y - self.y)/10)

class Point():
    def __init__(self, x, y):
        self.x
        self.y


if __name__ == "__main__":

    joint = Joint("hand", 7)
    chaser = ChaserBall()
    print(joint)

    print(joint.x)

