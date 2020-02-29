import cv2
import numpy as np
import random

class Element():
    """
    Element is an entitity that lives in the animation
    and can be drawn
    """
    pass

    def __init__(self, position=None, name=None):
        
        if position is None:
            self.position = np.array([0, 0], np.float32)
        else:
            self.position = position.astype(np.float32)
        
        if name is None:
            self.name = "element"
        else:
            self.name = name

    def update(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError


class Mover(Element):
    """
    Element that contains the movement eq
    """

    def __init__(self, velocity=None, mass=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if velocity is None:
            self.velocity = np.array([0, 0], np.float32)
        else:
            self.velocity = velocity

        if mass is None:
            self.mass = 1
        else:
            self.mass = mass

        self.forces = []
        self.acceleration = np.array([0, 0], np.float32)
        

    def move(self):
        for force in self.forces:
            self.acceleration += force / self.mass

        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        self.forces = []

    def add_forces(self, forces):
        self.forces.extend(forces)

    def update(self):
        self.move()


class RandomMover(Mover):
    """
        apply random force to a mover to get a random walker
    """
    def __init__(self, velocity=None, mass=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update(self):
        random_force = np.array([
            random.choice([-1, 0, 1]), 
            random.choice([-1, 0, 1])],
        np.float64) / 10

        self.add_forces([random_force])
        self.move()


class Chaser(Mover):
    """
        chase an object using steer velocity
    """
    def __init__(self, 
                 chase_to, 
                 land_distance=None,  # distance to start decreasing speed to land properly
                 min_distance=None,   # min distance to chase to move
                 max_speed=None,      # max speed is reached if aligned with target  
                 max_force=None,      # larger force helps redirecting trajectory
                 mass=None,
                 *args, **kwargs

    ):
        super().__init__(*args, **kwargs)
        self.chase_to = chase_to

        if land_distance is None:
            self.land_distance = 70

        if min_distance is None:
            self.min_distance = 10
        
        if max_speed is None:
            self.max_speed = 5

        if max_force is None:
            self.max_force = 8

        if mass is None:
            self.mass = 7

    def update_distance_to_chase(self):
        self.distance_to_chase = self.chase_to.position - self.position
        self.distance_to_chase_norm = np.linalg.norm(self.distance_to_chase)
        self.distance_to_chase_unit = self.distance_to_chase / self.distance_to_chase_norm


    def get_steer_force(self):
        """
            steer force with land distance
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


    def update(self):
        self.update_distance_to_chase()
        steer_force = self.get_steer_force()
        self.add_forces([steer_force])
        self.move()


class MiddlePoint(Element):

    def __init__(self, point_a, point_b, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.point_a = point_a
        self.point_b = point_b


    def update(self):

        self.point_to_point_distance = self.point_b.position - self.point_a.position
        self.point_to_point_distance_norm = np.linalg.norm(self.point_to_point_distance)

        if self.point_to_point_distance_norm > 0:
            self.point_to_point_distance_unit = self.point_to_point_distance / self.point_to_point_distance_norm
            self.position = self.point_a.position + self.point_to_point_distance_unit * (self.point_to_point_distance_norm / 2)
        else:
            self.position = self.point_a.position




class Circle(Element):
    """
        Element that moves according to euler's integration
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def draw(self, image, allow_transparency):
        draw_circle(image, self.position, 40, (0,255,0), -1)
        return image



class RandomCircle(RandomMover, Circle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ChaserCircle(Chaser, Circle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, image, allow_transparency):
        image = super().draw(image, allow_transparency)
        draw_line(image, self.position, self.chase_to.position, (0,0,255), 10)
        return image


class MiddleCircle(MiddlePoint, Circle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def draw_circle(image, center, radius, color, width):

    x = np.rint(center[0]).astype(np.int64)
    y = np.rint(center[1]).astype(np.int64)
    radius = np.rint(radius).astype(np.int64)
    cv2.circle(image, (x, y), radius, color, width)

def draw_line(image, pt1, pt2, color, width):
    x_1 = np.rint(pt1[0]).astype(np.int64)
    y_1 = np.rint(pt1[1]).astype(np.int64)
    x_2 = np.rint(pt2[0]).astype(np.int64)
    y_2 = np.rint(pt2[1]).astype(np.int64)

    cv2.line(image, (x_1, y_1), (x_2, y_2), color, width)

if __name__ == "__main__":

    e = Element("")
    e.draw()

    print("hello")