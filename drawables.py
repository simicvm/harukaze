import cv2
import random
import numpy as np
import time

DEBUG = False

class Drawable():
    def __init__(self, position, name):
        self.name = name
        self.position = position.astype(np.float64)


class ChaserSpinningMiddleHands(Drawable):
    """
        contains update method for chasing ball (to anchor)
    """

    step = 0

    """ 

    n_circles_parameter = 1 # times hand_to_hand distance 
    min_n_circles = 5
    
    max_angular_speed = 0.2

    center_radius_parameter = 1
    min_center_radius = 5
    max_center_radius = 100

    circle_size_parameter = 1
    min_circle_size = 5
    max_circle_size = 10

    """    

    # drawing parameters
    n_circles_parameter = 1 # times hand_to_hand distance 
    min_n_circles = 5
    max_n_circles = 100
    n_circles = 1
    max_n_circles_delta = 5
    
    max_angular_speed = 0.02 #0.015 * np.pi

    center_radius_parameter = 1.3
    min_center_radius = 2
    max_center_radius = 200

    circle_size_parameter = 0.004
    min_circle_size = 5
    max_circle_size = 30

    color_a = (0, 0, 190)
    color_b = (0, 0, 0)

    # physics parameters
    position = np.array([0., 0])
    velocity = np.array([0., 0])
    acceleration = np.array([0., 0])
    forces = []
    mass = 5

    max_speed = 6
    max_force = 7
    min_distance = 5

    land_distance = 50


    def __init__(self, left_hand, right_hand, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_hand = left_hand
        self.right_hand = right_hand
        self.update()

    def draw(self, frame, allow_transparency):

        if DEBUG:
            self._draw_circle(frame, self.position, 50, self.color, -1)
            self._draw_circle(frame, self.chase_to, 10, (255, 255, 255), -1)
        

        for i in range(self.n_circles, 0, -1): # we want to print bigger circles first

            angle = 2*np.pi*(1.0 * i / self.n_circles) * self.step * self.angular_speed

            if i%2:
                color = self.color_a
            else:
                color = self.color_b

            center = self.position + pol2cart(self.center_radius, angle)
            size = self.circle_size * i
            
            if allow_transparency:
                overlay = frame.copy()
                cv2.circle(overlay, center, size, color, -1)
                alpha = 1 - (i/self.n_circles)
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
            else:
                self._draw_circle(frame, center, size, color, -1)

        return frame

    def update_chase(self):
        """
            finding the point between two (right and left hand positions)
        """
        self.hand_to_hand_distance = self.right_hand.position - self.left_hand.position
        self.hand_to_hand_distance_norm = np.linalg.norm(self.hand_to_hand_distance)

        if self.hand_to_hand_distance_norm > 0:
            self.distance_unit = self.hand_to_hand_distance / self.hand_to_hand_distance_norm
            self.chase_to = self.left_hand.position + self.distance_unit * (self.hand_to_hand_distance_norm / 2)
        else:
            self.chase_to = self.left_hand.position

        self.distance_to_chase = self.chase_to - self.position
        self.distance_to_chase_norm = np.linalg.norm(self.distance_to_chase)
        self.distance_to_chase_unit = self.distance_to_chase / self.distance_to_chase_norm

    def update_drawing_parameters(self):
        
        new_n_circles = max(
            int(self.hand_to_hand_distance_norm/self.n_circles_parameter), 
            self.min_n_circles
        )

        new_n_circles = min(new_n_circles, self.max_n_circles)

        if abs(new_n_circles - self.n_circles) < self.max_n_circles_delta:
            self.n_circles = new_n_circles
        else:
            self.n_circles += self.max_n_circles_delta * np.sign(new_n_circles - self.n_circles)

        self.angular_speed = self.max_angular_speed

        center_radius = self.center_radius_parameter * self.hand_to_hand_distance_norm
        self.center_radius = max(center_radius, self.min_center_radius)
        self.center_radius = min(center_radius, self.max_center_radius)

        circle_size = self.hand_to_hand_distance_norm * self.circle_size_parameter
        circle_size = min(circle_size, self.max_circle_size)
        circle_size = max(circle_size, self.min_circle_size)
        self.circle_size = circle_size
        
    def update(self):
        self.update_chase()
        self.update_position()
        self.update_drawing_parameters()
        self.step += 1

    def get_steer_force(self):
        """
            steer force 
        """

        if self.distance_to_chase_norm < self.min_distance:
            return np.array([0, 0])
        
        if self.distance_to_chase_norm < self.land_distance:
            self.speed = np.interp(self.distance_to_chase_norm, [0, self.land_distance], [0, self.max_speed])
        else:
            self.speed = self.max_speed

        desired_velocity = self.distance_to_chase_unit * self.speed

        steer_force = desired_velocity - self.velocity
        steer_force_norm = np.linalg.norm(steer_force)
        
        if steer_force_norm > self.max_force:
            steer_force = steer_force / steer_force_norm * self.max_force
        
        return steer_force

    def update_position(self):

        self.forces.append(self.get_steer_force())

        for force in self.forces:
            print(force)
            self.acceleration += force / self.mass

        self.velocity += self.acceleration
        self.position += self.velocity

        self.acceleration *= 0
        self.forces = []

    @staticmethod
    def _draw_circle(frame, center, size, color, width):
        x = np.rint(center[0]).astype(np.int64)
        y = np.rint(center[1]).astype(np.int64)
        size = np.rint(size).astype(np.int64)
        print(x, y, size)
        cv2.circle(frame, (x, y), size, color, width)


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array([x, y])


if __name__ == "__main__":

    spinning_chaser_ball = SpinningChaserBall(0, 1, None, "ChaserSpinning")

    spinning_chaser_ball.draw()
    spinning_chaser_ball.update()

    spinning_random_ball = SpinningRandomBall(0, 1, "RandomSpinning")
    spinning_random_ball.draw()
    spinning_random_ball.update()
