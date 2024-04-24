import pygame
from pygame.locals import *
from Entity import Entity

class ExitGate(Entity):
    def __init__(self, position):
        super().__init__(position)
        self.is_powered = False
        self.activation_time = 15  # Time in seconds for survivors to activate the exit gate
        self.activating_survivor = None  # Reference to the survivor activating the exit gate

    def activate(self, survivor):
        if not self.is_powered:
            self.activating_survivor = survivor
            self.activation_time -= 1  # Decrement activation time by 1 unit per frame (adjust as needed)
            if self.activation_time <= 0:
                self.is_powered = True
        else:
            # Exit gate is already powered, no need to activate
            pass

    def draw(self, screen):
        color = (0, 255, 255) if self.is_powered else (128, 128, 128)
        pygame.draw.rect(screen, color, (int(self.position[0]), int(self.position[1]), 20, 20))