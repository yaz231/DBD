import numpy as np
class Player:
    def __init__(self, position=(0, 0)):
        self.position = np.array(position)

    def move(self, direction):
        # Move the player in the specified direction
        direction = np.array(direction)
        self.position += direction