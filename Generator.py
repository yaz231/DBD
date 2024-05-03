import pygame
from pygame.locals import *

from Entity import Entity

class Generator(Entity):
    def __init__(self, position):
        super().__init__(position)
        self.is_working = False
        self.progress = 0
        self.is_completed = False
        self.is_being_repaired = False
        self.repair_timer = 100  # Time in seconds for one survivor to repair the generator
        self.repairing_survivor = None  # Reference to the survivor repairing the generator

    def repair(self, survivor):
        if not self.is_working:
            self.repairing_survivor = survivor
            self.is_being_repaired = True
            self.progress += 1  # Increment progress by 1 unit per frame (adjust as needed)
            if self.progress >= self.repair_timer:
                self.is_working = True
                self.progress = 0
        else:
            # Generator is already working, no need to repair
            self.is_completed = True

    def update(self):
        pass

    def stop_repair(self):
        self.repairing_survivor = None

    def draw(self, screen):
        """
        Draws the generator with a color based on its repair progress.
        """

        # Define colors for different generator states
        unworked_color = (128, 128, 128)
        completed_color = (255, 255, 255)

        # Color selection based on progress
        if self.progress == 0.0:
            color = unworked_color
        elif self.progress == 1.0:
            color = completed_color
        else:
            # Interpolate color for in-between stages
            progress_percent = self.progress / self.repair_timer
            color = self.interpolate_color(unworked_color, completed_color, progress_percent)

        pygame.draw.rect(screen, color, (int(self.position[0]), int(self.position[1]), 20, 20))

    def interpolate_color(self, color1, color2, factor):
        """
        Interpolates between two colors based on a factor (0.0 to 1.0).

        Args:
            color1: The first color as a tuple (R, G, B).
            color2: The second color as a tuple (R, G, B).
            factor: The interpolation factor (0.0 to 1.0).

        Returns:
            A tuple representing the interpolated color (R, G, B).
        """
        return tuple([int(self.color_lerp(c1, c2, factor)) for c1, c2 in zip(color1, color2)])

    def color_lerp(self, color1, color2, factor):
        """
        Linearly interpolates between two color values.

        Args:
            color1: The first color value.
            color2: The second color value.
            factor: The interpolation factor (0.0 to 1.0).

        Returns:
            The interpolated color value.
        """
        return color1 + (color2 - color1) * factor
