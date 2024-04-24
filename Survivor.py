import pygame
from pygame.locals import *
import random
import math

import time
import Generator
from Entity import Entity
import Killer
class Survivor(Entity):
    def __init__(self, name, position, game):
        super().__init__(position, )
        self.name = name
        self.game = game
        self.state = "healthy"
        self.dead = False
        self.is_downed = False
        self.hooked_count = 0
        self.speed = 4
        self.bleedout_times = [60, 30]
        self.bleedout_time = self.bleedout_times[self.hooked_count]
        self.velocity = [0, 0]
        self.interaction_start_time = None
        self.interaction_target = None
        self.interaction_range = 5
        self.explored = set()
        self.angle_of_vision = 90
        self.max_vision_distance = 150
        self.direction = 0

    def turn_randomly(self):
        # Randomly decide whether to turn left or right
        if random.random() < 0.1:  # Adjust the probability as needed
            # Turn left or right randomly
            self.direction += random.choice([-1, 1]) * math.radians(15)  # Adjust the turning angle as needed

    def repair_generator(self, generator_position):
        if abs(generator_position[0] - self.position[0]) <= 10 and abs(generator_position[1] - self.position[1]) <= 10:
            print(f"{self.name} is repairing the generator.")

    def explore(self, area):
        # Update explored areas
        self.explored.add(area)

    def stop(self):
        # Stop the survivor's movement
        self.velocity = [0, 0]

    def get_angle_in_degrees(self):
        return math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def get_relative_angle(self, angle):
        relative_angle = angle - self.get_angle_in_degrees()
        if relative_angle < -180:
            relative_angle += 360
        elif relative_angle > 180:
            relative_angle -= 360
        return relative_angle

    def interact(self, target):
        if isinstance(target, Survivor):
            if target.state == "injured" and self.state == "healthy":
                self.interaction_start_time = time.time()
                self.interaction_target = target
                # If the target is a downed survivor, start reviving
            elif target.state == "downed" and self.state == "healthy":
                self.interaction_start_time = time.time()
                self.interaction_target = target

            # If the target is a survivor and the target is hooked, the current survivor can attempt to free them
            elif target.state == "hooked":
                self.free_from_hook()
        elif isinstance(target, Generator):
            target.repair(self)

    def free_from_hook(self):
        if self.state == "hooked" and self.hooked_hook is not None:
            hooked_hook = self.hooked_hook
            hooked_hook.free()
            self.state = "healthy"
            self.is_downed = False
            self.hooked_hook = None

    def take_hit(self):
        if self.state == "healthy":
            self.state = "injured"
        elif self.state == "injured":
            self.state = "downed"
            self.is_downed = True

    def heal(self):
        # If interaction time has elapsed, heal the target survivor
        if self.interaction_target is not None and self.state == "healthy":
            current_time = time.time()
            if current_time - self.interaction_start_time >= 5:
                self.interaction_target.state = "healthy"
                self.interaction_target = None
                self.interaction_start_time = None

    def revive(self):
        # If interaction time has elapsed, revive the target survivor
        if self.interaction_target is not None and self.state == "healthy":
            current_time = time.time()
            if current_time - self.interaction_start_time >= 10:
                self.interaction_target.state = "injured"
                self.interaction_target.is_downed = False
                self.interaction_target = None
                self.interaction_start_time = None

    def move(self, direction):
        # Update survivor's direction
        self.direction = direction

        # Move survivor based on direction
        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def wander(self):
        # print("CURRENT DIRECTION: ", self.direction)
        # Randomly adjust the killer's direction
        new_direction = self.direction + random.randint(-30, 30)
        self.direction = new_direction

        # Calculate velocity components
        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        # Move killer based on velocity
        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def update(self):
        # Keep the survivor within the bounds of the screen
        self.position[0] = max(0, min(self.position[0], self.game.width))
        self.position[1] = max(0, min(self.position[1], self.game.height - 100))

        # # Move away from the killer if within vision range
        # for entity in self.game.entities:
        #     if isinstance(entity, type(Killer)):
        #         if self.check_vision(entity.position):
        #             self.move_away_from_killer(entity.position)

        self.wander()

    def move_away_from_killer(self, killer_position):
        dx = self.position[0] - killer_position[0]
        dy = self.position[1] - killer_position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            dx /= distance
            dy /= distance

        self.position[0] = self.position[0] + dx * self.speed
        self.position[1] = self.position[1] + dy * self.speed

    def calculate_vision_cone(self):
        vision_cone = []
        survivor_diretion = self.direction
        for angle in range(int(survivor_diretion - self.angle_of_vision // 2),
                           int(survivor_diretion + self.angle_of_vision // 2 + 1)):
            angle_radians = math.radians(angle)
            dx = math.cos(angle_radians)
            dy = math.sin(angle_radians)
            vision_cone.append((dx * self.max_vision_distance, dy * self.max_vision_distance))

        return vision_cone

    def check_vision(self, entity_position):
        dx = entity_position[0] - self.position[0]
        dy = entity_position[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            return False

        if distance > self.max_vision_distance:
            return False

        angle_to_entity = math.degrees(math.atan2(dy, dx))
        survivor_angle = self.direction
        relative_angle = angle_to_entity - survivor_angle

        if abs(relative_angle) <= self.angle_of_vision / 2:
            return True
        else:
            return False

    def draw(self, screen):
        if self.state == "healthy":
            color = (0, 255, 0)  # Green for healthy survivor
        elif self.state == "injured":
            color = (255, 165, 0)  # Orange for injured survivor
        elif self.state == "downed":
            color = (255, 0, 0)  # Red for downed survivor
        pygame.draw.circle(screen, color, (int(self.position[0]), int(self.position[1])), 10)

        # Draw vision cone
        vision_cone_color = (0, 255, 0, 100)  # Semi-transparent green
        vision_cone = self.calculate_vision_cone()
        for dx, dy in vision_cone:
            end_point = (self.position[0] + dx,
                         self.position[1] + dy)
            pygame.draw.line(screen, vision_cone_color, self.position, end_point, 1)