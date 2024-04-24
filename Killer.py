import pygame
from pygame.locals import *
from random import randint
import math

import Survivor
from Entity import Entity

class Killer(Entity):
    def __init__(self, name, position, game):
        super().__init__(position)
        self.name = name
        self.game = game
        self.speed = 3
        self.velocity = [0, 0]
        self.chase_speed_increase = 0.3
        self.direction = 0
        self.is_chasing = False
        self.chase_timer = 0
        self.interaction_range = 5
        self.chase_range = 30
        self.explored = set()
        self.angle_of_vision = 90
        self.max_vision_distance = 200

    def patrol_around_generator(self, generator_position):
        dx = randint(-1, 1)
        dy = randint(-1, 1)
        self.update_position(dx, dy)

    def wander(self):
        # print("CURRENT DIRECTION: ", self.direction)
        # Randomly adjust the killer's direction
        new_direction = self.direction + randint(-30, 30)
        self.direction = new_direction

        # Calculate velocity components
        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        # Move killer based on velocity
        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def chase_survivor(self, survivor_position):
        dx = survivor_position[0] - self.position[0]
        dy = survivor_position[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance <= self.max_vision_distance:
            if distance != 0:
                dx /= distance
                dy /= distance
            self.update_position(dx, dy)

    def move_towards(self, target):
        dx = target.position[0] - self.position[0]
        dy = target.position[1] - self.position[1]
        angle = math.degrees(math.atan2(dy, dx))

        self.direction = angle

        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def update(self):
        self.position[0] = max(0, min(self.position[0], self.game.width))
        self.position[1] = max(0, min(self.position[1], self.game.height - 100))

        seen_survivors = []

        for survivor in self.game.survivors:
            if self.check_vision_cone(survivor.position):
                print(f"{self.name} sees {survivor.name}")
                seen_survivors.append(survivor)

        if seen_survivors:
            nearest_survivor = min(seen_survivors, key=lambda s: self.find_distance(s.position))
            self.move_towards(nearest_survivor)

        else:
            self.wander()

    def find_distance(self, target_position):
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance

    def update_position(self, screen_width, screen_height):
        self.position[0] += self.velocity[0] * self.speed
        self.position[1] += self.velocity[1] * self.speed

        self.position[0] = max(0, min(self.position[0], screen_width))
        self.position[1] = max(0, min(self.position[1], screen_height))

    def increase_chase_speed(self):
        self.speed += self.chase_speed_increase

    def reset_chase_timer(self):
        self.chase_timer = 0

    def update_chase_timer(self, dt):
        self.chase_timer += dt

    def explore(self, area):
        self.explored.add(area)


    def get_angle_in_degrees(self):
        return math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def get_relative_angle(self, angle):
        relative_angle = angle - self.get_angle_in_degrees()
        if relative_angle < -180:
            relative_angle += 360
        elif relative_angle > 180:
            relative_angle -= 360
        return relative_angle

    def attack(self, target):
        target.take_hit()

    def hook(self, target, hook):
        if not hook.is_occupied:
            hook.occupy(target)
            target.state = "hooked"
            target.hooked_hook = hook
            target.position = hook.position

    def calculate_vision_cone(self):
        vision_cone = []
        killer_direction = self.direction
        for angle in range(int(killer_direction - self.angle_of_vision // 2),
                           int(killer_direction + self.angle_of_vision // 2 + 1)):
            angle_radians = math.radians(angle)
            dx = math.cos(angle_radians)
            dy = math.sin(angle_radians)
            vision_cone.append((dx * self.max_vision_distance, dy * self.max_vision_distance))

        return vision_cone

    def check_vision_cone(self, entity_position):
        dx = entity_position[0] - self.position[0]
        dy = entity_position[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance == 0:
            return False

        if distance > self.max_vision_distance:
            return False

        angle_to_entity = math.degrees(math.atan2(dy, dx))
        killer_angle = self.get_angle_in_degrees()
        relative_angle = self.get_relative_angle(angle_to_entity)

        if abs(relative_angle) <= self.angle_of_vision / 2:
            return True
        else:
            return False

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.position[0]), int(self.position[1])), 10)

        vision_cone_color = (255, 0, 0, 100)
        vision_cone = self.calculate_vision_cone()
        for dx, dy in vision_cone:
            end_point = (self.position[0] + dx,
                         self.position[1] + dy)
            pygame.draw.line(screen, vision_cone_color, self.position, end_point, 1)
