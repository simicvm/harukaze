import cv2
import random
import numpy as np


class Drawable():
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name


class Chaser(Drawable):
    """
        contains update method for chasing ball (to anchor)
    """

    speed = 10

    def __init__(self, chase_to, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chase_to = chase_to

    def update(self):
        if self.chase_to is not None:
            self.x += int((self.chase_to.x - self.x)/10)
            self.y += int((self.chase_to.y - self.y)/10)


class Fixed(Drawable):
    """
        contains update method for fixed ball to an anchor
    """
    def __init__(self, fixed_to, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixed_to = fixed_to

    def update(self):
        if self.fixed_to is not None:
            self.x = self.fixed_to.x
            self.y = self.fixed_to.y


class Random(Drawable):
    """
        contains update method for random walking ball
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self):
        self.x += random.choice(range(-10, 10))
        self.y += random.choice(range(-10, 10))


class Spinning(Drawable):
    """
        contains draw method for spinning ball
    """

    # n_circles = 20
    n_circles = 100
    step = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, frame):
        overlay = frame.copy()

        for i in range(self.n_circles, 0, -1):
            angle = 2*np.pi*(1.0 * i / self.n_circles) * self.step / 2
            
            if i%2:
                color = (0, 0, 230)
            else:
                color = (0, 0, 0)

            x, y = pol2cart(10, angle)
            center = (int(self.x + x), int(self.y + y))

            size = 3*i

            cv2.circle(overlay, center, size, color, -1)

            alpha = 1 - (i/self.n_circles)
            print(size, alpha)
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        self.step += 1

        exit()

        return frame


class SpinningChaserBall(Chaser, Spinning):
    def __init__(self, x, y, chase_to, name):
        super().__init__(x=x, y=y, chase_to=chase_to, name=name)


class SpinningFixedBall(Fixed, Spinning):
    def __init__(self, x, y, fixed_to, name):
        super().__init__(x=x, y=y, fixed_to=fixed_to, name=name)


class SpinningRandomBall(Random, Spinning):
    def __init__(self, x, y, name):
        super().__init__(x=x, y=y, name=name)


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)


if __name__ == "__main__":

    spinning_chaser_ball = SpinningChaserBall(0, 1, None, "ChaserSpinning")

    spinning_chaser_ball.draw()
    spinning_chaser_ball.update()

    spinning_random_ball = SpinningRandomBall(0, 1, "RandomSpinning")
    spinning_random_ball.draw()
    spinning_random_ball.update()
