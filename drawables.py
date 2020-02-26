import cv2
import random
import numpy as np
import time

DEBUG = False

class Drawable():
    def __init__(self, position, name):
        # self.x = x
        # self.y = y
        self.name = name
        self.position = position.astype(np.float64)

# class Chaser(Drawable):
#     """
#         contains update method for chasing ball (to anchor)
#     """

#     speed = 0.25

#     def __init__(self, chase_to, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.chase_to = chase_to

#     def update(self):
#         if self.chase_to is not None:
#             self.x += int((self.chase_to.x - self.x)*self.speed)
#             self.y += int((self.chase_to.y - self.y)*self.speed)


# class ChaserSpinningMiddleHands(Drawable):
#     """
#         contains update method for chasing ball (to anchor)
#     """

#     speed = 0.2

#     n_circles = 30
#     step = 0
#     angular_speed = -0.2
#     center_radius = 100
#     size_parameter = 1

#     hand_to_hand = 0
#     hand_to_hand_sensitivity = 700

#     def __init__(self, left_hand, right_hand, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.left_hand = left_hand
#         self.right_hand = right_hand


#     def draw(self, frame, allow_transparency):

#         # time.sleep(1)
#         self.n_circles = int(self.hand_to_hand/3) + 1
#         print(self.hand_to_hand)

#         for i in range(self.n_circles, 0, -1):
            
#             angle = 2*np.pi*(1.0 * i / self.n_circles) * self.step * self.angular_speed

#             if i%2:
#                 color = (0, 0, 190)
#             else:
#                 color = (0, 0, 0)

#             x, y = pol2cart(self.center_radius * self.hand_to_hand / 100, angle)
#             center = (int(self.position[0] + x), int(self.position[1] + y))

#             size = int(self.size_parameter * i * self.hand_to_hand / 100)
            
            

#             if allow_transparency:
#                 overlay = frame.copy()
#                 cv2.circle(overlay, center, size, color, -1)
#                 alpha = 1 - (i/self.n_circles)
#                 frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
#             else:
#                 cv2.circle(frame, center, size, color, -1)

#         self.step += 1

#         return frame


#     def update(self):
        
#         new_hand_to_hand = np.linalg.norm(self.left_hand.position-self.right_hand.position)
#         delta_hand_to_hand = new_hand_to_hand - self.hand_to_hand

#         if abs(delta_hand_to_hand) < self.hand_to_hand_sensitivity:
            
#             if new_hand_to_hand > 100:
#                 self.hand_to_hand += delta_hand_to_hand * 0.2
#             else:
#                 self.hand_to_hand += delta_hand_to_hand * 0.8
#         else:
#             print(delta_hand_to_hand)
#             exit()


#         if self.left_hand.position[0] >= self.right_hand.position[0]:
#             chase_to_x = self.right_hand.position[0] + (self.left_hand.position[0] - self.right_hand.position[0])/2
#         else: 
#             chase_to_x = self.left_hand.position[0] + (self.right_hand.position[0] - self.left_hand.position[0])/2

#         if self.left_hand.position[1] >= self.right_hand.position[1]:
#             chase_to_y = self.right_hand.position[1] + (self.left_hand.position[1] - self.right_hand.position[1])/2
#         else: 
#             chase_to_y = self.left_hand.position[1] + (self.right_hand.position[1] - self.left_hand.position[1])/2
        

#         self.position[0] += int((chase_to_x - self.position[0])*self.speed)
#         self.position[1] += int((chase_to_y - self.position[1])*self.speed)
#         self.angular_speed = self.position[1]/400
#         # print(self.position[1]/1000)

#         # right_hand_direction = self.right_hand.position[0] - self.right_hand.previous_position[0] 
#         # left_hand_direction = self.left_hand.position[0] - self.left_hand.previous_position[0]

#         # if right_hand_direction > 0 and left_hand_direction < 0:
#         #     self.angular_speed *= -1

#         # print(left_hand_direction, right_hand_direction)
#         # time.sleep(0.1)



class ChaserSpinningMiddleHands(Drawable):
    """
        contains update method for chasing ball (to anchor)
    """

    step = 0



    # drawing parameters
    n_circles_parameter = 1 # times hand_to_hand distance 
    min_n_circles = 5
    
    max_angular_speed = 0.2

    center_radius_parameter = 1
    min_center_radius = 5
    max_center_radius = 100

    circle_size_parameter = 1
    min_circle_size = 5
    max_circle_size = 10

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


    @staticmethod
    def _draw_circle(frame, center, size, color, width):
        x = np.rint(center[0]).astype(np.int64)
        y = np.rint(center[1]).astype(np.int64)
        cv2.circle(frame, (x, y), size, color, width)

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

            x, y = pol2cart(self.center_radius, angle)
            center = (int(self.position[0] + x), int(self.position[1] + y))

            size = int(self.size_parameter * i * self.hand_to_hand / 100)
            
            

            if allow_transparency:
                overlay = frame.copy()
                cv2.circle(overlay, center, size, color, -1)
                alpha = 1 - (i/self.n_circles)
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
            else:
                print(size)
                # exit()
                cv2.circle(frame, center, size, color, -1)

        return frame

    def update_chase(self):
        """
            finding the point between two (right and left hand positions)
        """
        self.hand_to_hand_distance = self.right_hand.position - self.left_hand.position
        self.hand_to_hand_distance_norm = np.linalg.norm(self.hand_to_hand_distance)

        if self.hand_to_hand_distance_norm > 0:
            distance_unit = hand_to_hand_distance / self.hand_to_hand_distance_norm
            self.chase_to = self.left_hand.position + distance_unit * (self.hand_to_hand_distance_norm / 2)
        else:
            self.chase_to = self.left_hand.position

        self.distance_to_chase = self.chase_to - self.position
        self.distance_to_chase_norm = np.linalg.norm(self.distance_to_chase)
        self.distance_to_chase_unit = self.distance_to_chase / self.distance_to_chase_norm


    def update_drawing_parameters(self):
        
        self.n_circles = max(
            int(self.hand_to_hand_distance_norm/self.n_circles_parameter), 
            self.min_n_circles
        )

        self.angular_speed = self.max_angular_speed

        center_radius = self.center_radius_parameter * self.hand_to_hand_distance_norm
        self.center_radius = max(center_radius, self.min_center_radius)
        self.center_radius = min(center_radius, self.max_center_radius)
        

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


        
        # if self.left_hand.position[0] >= self.right_hand.position[0]:
        #     self.chase_to[0] = self.right_hand.position[0] + (self.left_hand.position[0] - self.right_hand.position[0])/2
        # else: 
        #     self.chase_to[0] = self.left_hand.position[0] + (self.right_hand.position[0] - self.left_hand.position[0])/2

        # if self.left_hand.position[1] >= self.right_hand.position[1]:
        #     self.chase_to[1] = self.right_hand.position[1] + (self.left_hand.position[1] - self.right_hand.position[1])/2
        # else: 
        #     self.chase_to[1] = self.left_hand.position[1] + (self.right_hand.position[1] - self.left_hand.position[1])/2
        
        # self.position[0] += int((chase_to[0] - self.position[0])*self.speed)
        # self.position[1] += int((chase_to[1] - self.position[1])*self.speed)

        # self.position += (chase_to - self.position)/10.

        
        # distance = self.chase_to - self.position
        # distance_norm = np.linalg.norm(distance)

        # if distance_norm > 0:
        #     direction = distance / distance_norm
        # else:
        #     direction = np.array([0, 0])

        # print("distance:{} direction:{}, distance_norm: {}".format(distance, direction, distance_norm))

        # velocity = direction * self.speed + direction * distance_norm/20
        # velocity_norm = np.linalg.norm(velocity)
        # print("velocity: {} velocity_norm: {}".format(velocity, velocity_norm))

        # acceleration = direction * distance_norm/20




        # if velocity_norm > self.max_velocity_norm:
        #     self.color = (255, 0, 0)
        #     velocity = velocity / velocity_norm * self.max_velocity_norm

        # elif velocity_norm < self.min_velocity_norm:
        #     self.color = (0, 255, 0)
        #     velocity = np.array([0.1, 0.1])
        #     # velocity = velocity / velocity_norm * self.min_velocity_norm
        # else:
        #     self.color = (0, 0, 255)

        # print(direction)
        # exit()
        # print(chase_to)
        # print(self.position)
        # print(distance)
        # print(distance/2)

        # self.position += (distance / 20).astype(np.int64)

        # print(self.position)
        # self.position += velocity

        # self.position += np.array([1, 1])

        # if np.sum(distance) > np.sum(self.max_distance):
        #     self.max_distance = distance

        # print("max distance: {}".format(self.max_distance))
        
        
        # distance = np.linalg.norm(self.position - chase_to)
        # direction = (self.position - chase_to)/distance



        # print(distance)
        # print(direction)
        # print(direction * distance)
        # print(self.position)
        # print(chase_to)
        # self.position = (self.position + direction * distance).astype(np.uint8)



        # print(self.position)
        # print()
        # self.position[0] = int(self.position[0])
        # self.position[1] = int(self.position[1])

        # # print(chase_to)

        # time.sleep(0.5)
        # if distance > 150:
        #     print("distance")
        #     print(np.linalg.norm(self.position - chase_to))
        #     time.sleep(1)

        # self.position += (chase_to - self.position) * self.speed 

    # def update(self):
        
    #     new_hand_to_hand = np.linalg.norm(self.left_hand.position-self.right_hand.position)
    #     delta_hand_to_hand = new_hand_to_hand - self.hand_to_hand

    #     if abs(delta_hand_to_hand) < self.hand_to_hand_sensitivity:
            
    #         if new_hand_to_hand > 100:
    #             self.hand_to_hand += delta_hand_to_hand * 0.2
    #         else:
    #             self.hand_to_hand += delta_hand_to_hand * 0.8
    #     else:
    #         print(delta_hand_to_hand)
    #         exit()

    #     self.update_position()
        

        
        # self.angular_speed = self.position[1]/400
        # print(self.position[1]/1000)

        # right_hand_direction = self.right_hand.position[0] - self.right_hand.previous_position[0] 
        # left_hand_direction = self.left_hand.position[0] - self.left_hand.previous_position[0]

        # if right_hand_direction > 0 and left_hand_direction < 0:
        #     self.angular_speed *= -1

        # print(left_hand_direction, right_hand_direction)
        # time.sleep(0.1)




# class Fixed(Drawable):
#     """
#         contains update method for fixed ball to an anchor
#     """
#     def __init__(self, fixed_to, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fixed_to = fixed_to

#     def update(self):
#         if self.fixed_to is not None:
#             self.x = self.fixed_to.x
#             self.y = self.fixed_to.y


# class Random(Drawable):
#     """
#         contains update method for random walking ball
#     """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def update(self):
#         self.x += random.choice(range(-10, 10))
#         self.y += random.choice(range(-10, 10))


# class Spinning(Drawable):
#     """
#         contains draw method for spinning ball
#     """

#     # n_circles = 20
#     n_circles = 30
#     step = 0
#     angular_speed = 1
#     center_radius = 100
#     size_parameter = 1

#     """
#     configurations:


#     center_radius: 100
#     size_parameter: 1
#     angular_speed: 1
#     n_circles: 30


#     """

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def draw(self, frame, allow_transparency):

#         for i in range(self.n_circles, 0, -1):

#             overlay = frame.copy()

#             angle = 2*np.pi*(1.0 * i / self.n_circles) * self.step * self.angular_speed

#             if i%2:
#                 color = (0, 0, 190)
#             else:
#                 color = (0, 0, 0)

#             x, y = pol2cart(self.center_radius, angle)
#             center = (int(self.x + x), int(self.y + y))

#             size = self.size_parameter*i

#             if allow_transparency:
#                 cv2.circle(overlay, center, size, color, -1)
#                 alpha = 1 - (i/self.n_circles)
#                 frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
#             else:
#                 cv2.circle(frame, center, size, color, -1)

#         self.step += 1

#         return frame


# class Katana():

#     katana_length = 100

#     def __init__(self, fixed_elbow, fixed_hand, name):
#         # self.elbow_x = fixed_elbow.x
#         # self.elbow_y = fixed_elbow.y

#         # self.elbow_x = fixed_elbow.x
#         # self.elbow_y = fixed_elbow.y
#         self.fixed_hand = fixed_hand
#         self.fixed_elbow = fixed_elbow
#         self.name = name

#     def update(self):
#         self.elbow_x = self.fixed_elbow.x
#         self.elbow_y = self.fixed_elbow.y

#         self.hand_x = self.fixed_hand.x
#         self.hand_y = self.fixed_hand.y

#     def draw(self, frame):
#         cv2.circle(frame, (self.elbow_x, self.elbow_y), 2, (255, 255, 255), -1)
#         cv2.circle(frame, (self.hand_x, self.hand_y), 2, (255, 255, 255), -1)

#         dx = self.hand_x - self.elbow_x
#         dy = self.hand_y - self.elbow_y

#         length = (dx*dx+dy*dy)**0.5

#         unit_x = dx/length
#         unit_y = dy/length

#         cv2.line(frame, (self.hand_x, self.hand_y), (self.elbow_x, self.elbow_y), (0, 0, 255), 10)


#         print(length)
#         # exit()
#         return frame


# class SpinningChaserBall(Chaser, Spinning):
#     def __init__(self, x, y, chase_to, name):
#         super().__init__(x=x, y=y, chase_to=chase_to, name=name)


# class SpinningChaserMiddleHands(ChaserMiddleHands, Spinning):
#     def __init__(self, x, y, left_hand, right_hand, name):
#         super().__init__(x=x, y=y, left_hand=left_hand, right_hand=right_hand, name=name)


# class SpinningFixedBall(Fixed, Spinning):
#     def __init__(self, x, y, fixed_to, name):
#         super().__init__(x=x, y=y, fixed_to=fixed_to, name=name)


# class SpinningRandomBall(Random, Spinning):
#     def __init__(self, x, y, name):
#         super().__init__(x=x, y=y, name=name)


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
