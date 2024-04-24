import pygame
from pygame.locals import *

from Entity import Entity

class Generator(Entity):
    def __init__(self, position):
        super().__init__(position)
        self.is_working = False
        self.progress = 0
        self.repair_speed = 10  # Time in seconds for one survivor to repair the generator
        self.repairing_survivor = None  # Reference to the survivor repairing the generator

    def repair(self, survivor):
        if not self.is_working:
            self.repairing_survivor = survivor
            self.progress += 1  # Increment progress by 1 unit per frame (adjust as needed)
            if self.progress >= self.repair_speed:
                self.is_working = True
                self.progress = 0
        else:
            # Generator is already working, no need to repair
            pass

    def stop_repair(self):
        self.repairing_survivor = None

    def draw(self, screen):
        color = (255, 255, 255) if self.is_working else (128, 128, 128)
        pygame.draw.rect(screen, color, (int(self.position[0]), int(self.position[1]), 10, 10))
