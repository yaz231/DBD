import pygame
from pygame.locals import *
import random
import math

import Survivor
from Entity import Entity

class Killer(Entity):
    def __init__(self, name, position, game, generator_positions):
        super().__init__(position)
        self.name = name
        self.game = game
        self.original_speed = 3
        self.reduced_speed = self.original_speed / 2
        self.speed = self.original_speed
        self.velocity = [0, 0]
        self.chase_speed_increase = 0.3
        self.direction = 0
        self.is_chasing = False
        self.chase_timer = 0
        self.interaction_range = 5
        self.chase_range = 30
        self.explored = set()
        self.angle_of_vision = 120
        self.max_vision_distance = 200
        self.target_survivor = None
        self.generator_positions = generator_positions
        self.generator_queue = self.initialize_queue(self.generator_positions)
        self.attack_timer = 0

    def initialize_queue(self, generator_positions):
        sorted_generators = sorted(generator_positions, key=lambda gen: self.find_distance(gen))
        return sorted_generators

    def patrol_around_generator(self):
        patrol_distance = 5  # Adjust this value to control the patrol radius

        # Find the closest generator from the queue head
        closest_generator = self.generator_queue[0]
        distance = self.find_distance(closest_generator)  # Replace with your distance calculation function
        if distance < patrol_distance:
            # Reached patrol distance, update queue
            current_generator_position = self.generator_queue[0]
            self.generator_queue.pop(0)  # Remove the visited generator
            self.generator_queue.append(current_generator_position)
        else:
            self.move_towards(closest_generator)


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

    def chase_survivor(self, survivor_position):
        dx = survivor_position[0] - self.position[0]
        dy = survivor_position[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if self.is_chasing and self.chase_timer >= 15:
            self.increase_chase_speed()

        if distance <= self.max_vision_distance:
            self.move_towards(survivor_position)

        if distance <= self.interaction_range:
            self.attack(self.target_survivor)

    def move_towards(self, target):
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        angle = math.degrees(math.atan2(dy, dx))

        self.direction = angle

        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def update(self):
        self.position[0] = max(0, min(self.position[0], self.game.width))
        self.position[1] = max(0, min(self.position[1], self.game.height - 100))

        self.target_survivor = None
        for survivor in self.game.survivors:
            if self.check_vision_cone(survivor.position):
                print(f"{self.name} sees {survivor.name}")
                # seen_survivors.append(survivor)
                self.target_survivor = survivor
                break

        if self.target_survivor is not None:
            self.is_chasing = True
            self.chase_timer += 1
            self.chase_survivor(self.target_survivor.position)
        else:
            self.is_chasing = False
            self.chase_timer = 0
            # Choose between patrolling or wandering (existing logic)
            if not self.is_chasing:
                if random.random() > 0.75:
                    self.wander()
                else:
                    self.patrol_around_generator()

        # Update reward based on actions (replace with your reward logic)
        if self.is_chasing:
            self.reward += 0.1  # Reward for chasing survivors (adjust value)
        elif self.is_moving():
            self.reward += 0.05  # Small reward for exploration

        # Apply slow down after hitting survivor
        if self.attack_timer > 0:
            self.speed = self.reduced_speed  # Reduce speed during attack timer
            self.attack_timer -= 1
        else:
            self.speed = self.original_speed  # Reset speed after slow down duration

        return self.get_state()

    def get_state(self):
        return {
            "name": self.name,
            "position": self.position,
            "is_chasing": self.is_chasing,
            "chase_timer": self.chase_timer,
            "target_survivor": self.target_survivor and self.target_survivor.name,
            # Add information about nearby survivors and generators based on your observation design
        }

    def is_moving(self):
        return self.velocity[0] != 0 or self.velocity[1] != 0

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
        print("SPEED INCREASE")
        self.speed += self.chase_speed_increase

    def reset_chase_timer(self):
        self.chase_timer = 0

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
        if self.find_distance(target.position) <= self.interaction_range:
            target.take_hit()
            print(f"{self.name} hits {target.name}!")
            self.attack_timer = 3  # Reset attack timer for slow down
            self.is_chasing = False
            self.reset_chase_timer()
            self.speed = self.reduced_speed


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
