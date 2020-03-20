import cv2
import numpy as np
import random

from collections import namedtuple

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

    def draw(self, frame, allow_transparency):
        raise NotImplementedError


class Mover(Element):
    """
    Element that contains the movement eq
    """

    def __init__(self, 
                 velocity=None, 
                 mass=1, 
                 *args, **kwargs
        ):

        super().__init__(*args, **kwargs)

        self.forces = []
        self.velocity = velocity if velocity is not None else np.array([0, 0], np.float32)
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
                 land_distance=70,  # distance to start decreasing speed to land properly
                 min_distance=10,   # min distance to chase to move
                 max_speed=5,      # max speed is reached if aligned with target  
                 max_force=8,      # larger force helps redirecting trajectory
                 mass=7,
                 *args, **kwargs

    ):
        super().__init__(*args, **kwargs)
        self.chase_to = chase_to
        self.land_distance = land_distance
        self.min_distance = min_distance
        self.max_speed = max_speed
        self.max_force = max_speed
        self.mass = mass


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

        self.point_to_point_distance = self.point_b.position - self.point_a.position
        self.point_to_point_distance_norm = np.linalg.norm(self.point_to_point_distance)

    def update(self):

        self.point_to_point_distance = self.point_b.position - self.point_a.position
        self.point_to_point_distance_norm = np.linalg.norm(self.point_to_point_distance)

        if self.point_to_point_distance_norm > 0:
            self.point_to_point_distance_unit = self.point_to_point_distance / self.point_to_point_distance_norm
            self.position = self.point_a.position + self.point_to_point_distance_unit * (self.point_to_point_distance_norm / 2)
        else:
            self.position = self.point_a.position

    def draw(self, frame, *args, **kwargs):
        return frame


class Spinner(Element):
    """
        Element that moves according to euler's integration
    """

    def __init__(self, 
                n_circles=20,
                angular_speed=0.02,
                center_radius=200,
                min_radius=2,
                colors=None,
                *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.n_circles = n_circles
        self.angular_speed = angular_speed
        self.center_radius = center_radius
        self.min_radius = min_radius

        # idea, alternate btw colors when there are only 2
        if colors is None: 
            self.colors = [(0, 0, 0), (0, 0, 200)]
        else:
            self.colors = colors

        self.step = 1
    

    def draw(self, frame, allow_transparency):
        for i in range(self.n_circles, 0, -1): # we want to print bigger circles first
            
            angle = 2 * np.pi * i * self.step * self.angular_speed / self.n_circles
            color = self.colors[i%len(self.colors)]
            center = self.position + pol2cart(self.center_radius, angle)
            size = self.min_radius*(i+1)
            draw_circle(frame, center, size, color, -1)

        self.step += 1

        return frame



class Tunnel(Element):
    """
        Element that moves according to euler's integration
    """

    def __init__(self, 
                n_squares=100,
                size=10,
                colors=None,
                *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.n_squares = n_squares
        self.size = size
        self.colors = colors if colors is not None else [(0,0,0), (0,150,0), (0, 100, 0)]
        

    def draw(self, frame, allow_transparency):
        
        for i in range(self.n_squares, 1, -1):
            r_1 = np.random.randint(5)
            r_2 = np.random.randint(5)
            r_3 = np.random.randint(3, 10)

            size_1 = self.size * i * r_1
            size_2 = self.size * i * r_2
            width = r_3
            color = self.colors[i%len(self.colors)]

            draw_rectangle(frame, self.position - size_1, self.position + size_1, color)
            draw_rectangle(frame, self.position - size_2, self.position + size_2, color, width)

        return frame



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


class ChaserSpinner(Chaser, Spinner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class ChaserTunnel(Chaser, Tunnel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TunnelMiddleHands(Tunnel, Chaser):

    def __init__(self, 
                 chase_to, 
                 tension=0.1,                      # control how fast length increases or decreases
                 n_squares_parameter=0.001,         # control how fast new circles are added
                 size_parameter=0.01, 
                 *args, **kwargs):
        
        super().__init__(chase_to=chase_to, *args, **kwargs)
        self.length = self.chase_to.point_to_point_distance_norm
        self.tension = tension
        self.n_squares_parameter = n_squares_parameter
        self.size_parameter = size_parameter


    def update(self, *args, **kwargs):

        new_length = self.chase_to.point_to_point_distance_norm 
        delta = new_length - self.length

        
        Chaser.update(self)
        self.length += self.tension * delta

        self.n_squares += int(delta*self.n_squares_parameter)
        self.size += delta*self.size_parameter


"""
n_circles_parameter = 0.01
center_radius_parameter = 0.05
tension = 0.1

n_circles = 20
angular_speed =  0.02
center_radius =  200
min_radius = 2
"""

class SpinnerMiddleHands(Spinner, Chaser):

    def __init__(self, 
                 chase_to, 
                 tension=0.1,                      # control how fast length increases or decreases
                 n_circles_parameter=0.01,         # control how fast new circles are added
                 center_radius_parameter=0.05, 
                 *args, **kwargs):
        
        super().__init__(chase_to=chase_to, *args, **kwargs)
        self.length = self.chase_to.point_to_point_distance_norm
        self.tension = tension
        self.n_circles_parameter = n_circles_parameter
        self.center_radius_parameter = center_radius_parameter


    def update(self, *args, **kwargs):

        new_length = self.chase_to.point_to_point_distance_norm 
        delta = new_length - self.length

        
        Chaser.update(self)
        self.length += self.tension * delta

        self.n_circles += int(delta*self.n_circles_parameter)
        self.center_radius += delta*self.center_radius_parameter
    

class Screen():
    def __init__(self, 
                 mode="horizontal",
                 color_a=None,
                 color_b=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs) 

<<<<<<< HEAD
        if mode == "horizontal":
            self.draw = self.horizontal_screen
        elif mode == "vertical":
            self.draw = self.vertical_screen
        else:
            raise NotImplementedError

=======
>>>>>>> 17e2bf30b355f084eca2e59a345cf43ac6bda004
        self.color_a = color_a 
        self.color_b = color_b 

    def vertical_screen(self, image, *args, **kwargs):
        h, w = image.shape[:2]

        if self.color_a is not None:
            draw_rectangle(image, (0,0), (self.position[0], h), self.color_a)
        if self.color_b is not None:
            draw_rectangle(image, (self.position[0], 0), (w, h), self.color_b)
<<<<<<< HEAD
=======

        return image
>>>>>>> 17e2bf30b355f084eca2e59a345cf43ac6bda004

        return image

    def horizontal_screen(self, image, *args, **kwargs):
        h, w = image.shape[:2]

        if self.color_a is not None:
            draw_rectangle(image, (0,0), (w, self.position[1]), self.color_a)
        if self.color_b is not None:
            draw_rectangle(image, (0, self.position[1]), (w, h), self.color_b)

        return image

    def flip_colors(self):
        self.color_a, self.color_b = self.color_b, self.color_a

    def draw(self, image, *args, **kwargs):
        # self.horizontal_screen(image)
        self.vertical_screen(image)
        return image


class ChaserScreen(Screen, Chaser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 


class AngledChaserScreen(ChaserScreen):
    def __init__(self, point_a, point_b, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.point_a = point_a
        self.point_b = point_b
        self.angle = angle_between(self.point_b.position - self.point_a.position, np.array([1, 0]))

    def update(self):
        ChaserScreen.update(self)
        self.angle = angle_between(self.point_b.position - self.point_a.position, np.array([1, 0]))

        print("angle", self.angle)
        # import time; time.sleep(1)

    def draw(self, image, *args, **kwargs):

        draw_line(image, self.point_a.position, self.point_b.position, (0,0,0), 5)
        # image = ChaserScreen.draw(self, image, *args, **kwargs)
        # image = rotate_image(image, (self.position[0], self.position[1]), np.pi)
        
        h, w = image.shape[:2]
        # rot_center = (500, 500)
        # rotation_matrix = cv2.getRotationMatrix2D(rot_center, 90, 1)
        # image = cv2.warpAffine(image, rotation_matrix, (w, h))

        # print("rotating {}".format(self.angle))

        # center_rot = [self.position[0], self.position[1]]
        x, y = [self.position[0], self.position[1]]

        black_image = np.zeros((h, w), np.uint8)

        draw_rectangle(black_image, (x - 100, y - 100), (x + 100, y + 100), (150, 250, 0))
        rotation_matrix = cv2.getRotationMatrix2D((x, y), 180/np.pi*self.angle, 1)
        black_image = cv2.warpAffine(black_image, rotation_matrix, (w, h))


        # black_image = cv2.warpAffine(image, rotation_matrix, (w, h))
        # rotation_matrix = cv2.getRotationMatrix2D((x, y), 180/np.pi*self.angle, 1)
        # image = cv2.warpAffine(image, rotation_matrix, (w, h))
        image[:, :, 2] += black_image

        return image



class DoubleScreen():
    def __init__(self, point_a, point_b):
        self.chaser_a = ChaserScreen(chase_to=point_a, color_a=(0,0,0))
        self.chaser_b = ChaserScreen(chase_to=point_b, color_b=(0,0,190))

    def draw(self, image, *args, **kwargs):
        image = self.chaser_b.draw(image, *args, **kwargs)
        image = self.chaser_a.draw(image, *args, **kwargs)
        return image

    def update(self):
        self.chaser_a.update()
        self.chaser_b.update()



def draw_rectangle(image, pt1, pt2, color, thickness=-1):
    x_1 = np.rint(pt1[0]).astype(np.int64)
    y_1 = np.rint(pt1[1]).astype(np.int64)

    x_2 = np.rint(pt2[0]).astype(np.int64)
    y_2 = np.rint(pt2[1]).astype(np.int64)

    cv2.rectangle(image, (x_1, y_1), (x_2, y_2), color=color, thickness=thickness)

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


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array([x, y])


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def rotate_image(image, rot_center, angle):
    h, w = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D(rot_center, angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))


    h, w = image.shape[:2]
    rot_center = (500, 500)
    rotation_matrix = cv2.getRotationMatrix2D(rot_center, 90, 1)
    color_image = cv2.warpAffine(image, rotation_matrix, (w, h))

    return rotated_image

if __name__ == "__main__":

    e = Element("")
    e.draw()

    print("hello")