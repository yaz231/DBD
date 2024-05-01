import pygame
from pygame.locals import *
import random
import math

import time
from Generator import Generator
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
        self.interaction_range = 2
        self.explored = []
        self.angle_of_vision = 90
        self.max_vision_distance = 150
        self.direction = 0

    def find_distance(self, target_position):
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance

    def turn_randomly(self):
        # Randomly decide whether to turn left or right
        if random.random() < 0.1:  # Adjust the probability as needed
            # Turn left or right randomly
            self.direction += random.choice([-1, 1]) * math.radians(15)  # Adjust the turning angle as needed

    def repair_generator(self, generator_position):
        if self.find_distance(generator_position) <= self.interaction_range:
            print(f"{self.name} is repairing the generator.")
            self.game.generators[generator_position].repair(self)  # Call the generator's repair method

    def generator_completed(self):
        # Update survivor logic after completing a generator
        # (e.g., play an animation, update score, etc.)
        print(f"Survivor {self.name} completed a generator!")  # Example placeholder

    def explore(self, area):
        # Update explored areas
        self.explored.append(area)
        print(f"{self.name} explored the generator at {area}.")

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
            if target.state == "injured" and self.state != "downed":
                self.interaction_start_time = time.time()
                self.interaction_target = target
                # If the target is a downed survivor, start reviving
            elif target.state == "downed" and self.state == "downed":
                self.interaction_start_time = time.time()
                self.interaction_target = target

            # If the target is a survivor and the target is hooked, the current survivor can attempt to free them
            elif target.state == "hooked":
                self.free_from_hook()

        if isinstance(target, Generator):
            if not target.is_being_repaired:
                # Check if interaction has just started (no previous interaction time)
                if self.interaction_start_time is None:
                    self.interaction_start_time = time.time()
                # Check if enough repair time has passed
                current_time = time.time()
                if current_time - self.interaction_start_time >= 60:  # 60 seconds repair time
                    target.repair_timer = 0  # Set repair timer to 0 (completed)
                    self.interaction_start_time = None  # Reset interaction time
                    self.generator_completed()  # Call function for completion logic

    def free_from_hook(self):
        if self.state == "hooked" and self.hooked_hook is not None:
            hooked_hook = self.hooked_hook
            hooked_hook.free()
            self.state = "injured"
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

    def move_towards(self, target):
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        angle = math.degrees(math.atan2(dy, dx))

        self.direction = angle

        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def wander(self):
        new_direction = self.direction + random.randint(-30, 30)
        self.direction = new_direction

        # Calculate velocity components
        velocity_x = math.cos(math.radians(self.direction)) * self.speed
        velocity_y = math.sin(math.radians(self.direction)) * self.speed

        # Move killer based on velocity
        self.position[0] += velocity_x
        self.position[1] += velocity_y

    def find_closest_seen_generator(self):
        # Sort generators by distance to the survivor
        self.game.generator_list.sort(key=lambda generator: self.find_distance(generator.position))

        # Find the first unseen generator within range
        for generator in self.game.generator_list:
            if isinstance(generator, Generator) and not generator.is_completed and self.check_vision(generator.position):
                return generator
        return None  # If no unseen generators in range

    def update(self):
        # Keep the survivor within the bounds of the screen
        self.position[0] = max(0, min(self.position[0], self.game.width))
        self.position[1] = max(0, min(self.position[1], self.game.height - 100))

        # Check for injured/downed survivors within vision range
        for other_survivor in self.game.survivors:
            if other_survivor is not self and self.check_vision(other_survivor.position):
                if other_survivor.state == "injured" and self.state == "healthy":
                    self.interact(other_survivor)  # Heal the injured survivor
                    break  # Stop after interacting with the first injured survivor in sight
                elif other_survivor.state == "downed" and self.state == "healthy":
                    self.interact(other_survivor)  # Revive the downed survivor
                    break  # Stop after interacting with the first downed survivor in sight

        # Check for killer within vision range
        if self.game.killer:
            if self.check_vision(self.game.killer.position):
                # Move away from the killer if generator is not fully repaired
                self.move_away_from_killer(self.game.killer.position)

        # Check for unseen generators within vision range
        for generator in self.game.entities:
            if isinstance(generator, Generator) and not generator.is_completed:
                closest_generator = self.find_closest_seen_generator()

                # Move towards generator until in interaction range
                if closest_generator and self.find_distance(closest_generator.position) > self.interaction_range:
                    self.move_towards(closest_generator.position)
                    print(f"{self.name} moving toward generator {closest_generator}!")
                # If in range, interact with the generator
                else:
                    self.interaction_target = closest_generator
                    self.interact(closest_generator)
                    break  # Stop after interacting with the first generator in range


        # Check previously explored generators (if no unseen found)
        for generator in self.explored:
            if isinstance(generator, Generator) and not generator.is_completed:
                if self.find_distance(generator.position) <= self.interaction_range:
                    self.interaction_target = generator  # Set generator as interaction target
                    break  # Stop after interacting with the first generator in range

        # Update repair progress for the generator being interacted with
        if self.interaction_target and isinstance(self.interaction_target, Generator):
            # Check how many survivors are interacting with this generator
            interacting_survivors = 0
            for survivor in self.game.survivors:
                if survivor.interaction_target == self.interaction_target:
                    interacting_survivors += 1

            # Update repair timer based on the number of interacting survivors
            repair_time_per_survivor = self.interaction_target.repair_timer / interacting_survivors
            self.interaction_target.repair_timer -= repair_time_per_survivor

            # Check if repair is complete
            if self.interaction_target.repair_timer <= 0:
                self.interaction_target.is_completed = True  # Mark generator as repaired
                for survivor in self.game.survivors:  # Clear interaction target for all survivors
                    if survivor.interaction_target == self.interaction_target:
                        survivor.interaction_target = None

        # If no interactions or danger detected, wander around
        if self.interaction_target is None:
            self.wander()
        else:
            self.stop()

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
            # Check for generator discovery if within vision
            if isinstance(entity_position, Generator) and entity_position not in self.explored:
                return True  # Generator is within vision and not explored yet
            else:
                return True  # Entity is within normal vision range
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