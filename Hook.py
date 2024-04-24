import pygame
from pygame.locals import *
import Survivor
from Entity import Entity

class Hook(Entity):
    def __init__(self, position):
        super().__init__(position)
        self.is_occupied = False
        self.occupying_survivor = None  # Reference to the survivor on the hook
        self.unhook_time = 5  # Time in seconds for another survivor to unhook the hooked survivor
        self.hook_time = 3  # Time in seconds for the killer to hook a survivor

    def occupy(self, survivor):
        self.is_occupied = True
        self.occupying_survivor = survivor

    def free(self):
        self.is_occupied = False
        self.occupying_survivor = None

    def update(self):
        if self.is_occupied:
            self.occupying_survivor.bleed_out_time -= 1  # Decrement bleed out time by 1 unit per frame (adjust as needed)
            if self.occupying_survivor.bleed_out_time <= 0:
                # Survivor has bled out, remove them from the hook
                self.free()

    def hook_survivor(self, survivor):
        if not self.is_occupied:
            self.occupy(survivor)
            survivor.state = 'hooked'
            survivor.hooked_count += 1
            if survivor.hooked_count == 3:
                survivor.dead = True
            else:
                survivor.bleedout_time = survivor.bleedout_times[survivor.hooked_count - 1]
            # Implement logic for hooking survivor (if needed)

    def draw(self, screen):
        color = (255, 255, 0) if not self.is_occupied else (255, 165, 0)  # Yellow if not occupied, orange if occupied
        pygame.draw.rect(screen, color, (int(self.position[0]), int(self.position[1]), 10, 10))
