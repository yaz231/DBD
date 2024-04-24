import pygame
from pygame.locals import *
import math
import random

from Survivor import Survivor
from Generator import Generator
from Killer import Killer
from Hook import Hook

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.entities = []
        self.survivors = []

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dead By RL")
        self.font = pygame.font.Font(None, 24)  # Choose a font and font size

    def add_entity(self, entity):
        self.entities.append(entity)
        if isinstance(entity, Survivor):
            self.survivors.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    def draw(self):
        self.screen.fill((0, 0, 0))  # Fill screen with black color
        for entity in self.entities:
            entity.draw(self.screen)

        # Draw legend
        legend_width = self.width
        legend_height = 100
        legend_x = 0
        legend_y = self.height - legend_height
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (legend_x, legend_y, legend_width, legend_height))  # Legend background

        self.draw_text("Legend:", legend_x + 10, legend_y + 10, (255, 255, 255))
        self.draw_text("Generator Complete: White Square", legend_x + 10, legend_y + 40, (255, 255, 255))
        self.draw_text("Generator Incomplete: Grey Square", legend_x + 10, legend_y + 70, (128, 128, 128))

        self.draw_text("Survivor: Green Circle", legend_x + self.width / 3 + 10, legend_y + 40, (0, 255, 0))
        self.draw_text("Killer: Red Circle", legend_x + self.width / 3 + 10, legend_y + 70, (255, 0, 0))

        self.draw_text("Unoccupied Hooks: Yellow Circle", legend_x + 2 * self.width / 3 + 10, legend_y + 40, (255, 255, 0))
        self.draw_text("Occupied Hooks: Orange Circle", legend_x + 2 * self.width / 3 + 10, legend_y + 70, (255, 165, 0))

        pygame.display.flip()

    def draw_text(self, text, x, y, color):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def update(self):
        # Update game logic
        for entity in self.entities:
            entity.update()
    def generate_random_position(self):
        return [random.randint(0, self.width), random.randint(0, self.height)]

    def is_collision(self, pos):
        for entity in self.entities:
            if math.sqrt((pos[0] - entity.position[0]) ** 2 + (pos[1] - entity.position[1]) ** 2) < 50:
                return True
        return False

    def get_entities_in_killer_vision(self):
        # Implement the logic to return entities within the killer's vision
        # This method should return a list of entities visible to the killer
        visible_entities = []
        for entity in self.entities:
            if isinstance(entity, Survivor) or isinstance(entity, Killer):
                if self.killer.check_vision_cone(entity.position):
                    visible_entities.append(entity)
        return visible_entities

    def initialize_game(self):
        for i in range(4):
            pos = self.generate_random_position()
            while self.is_collision(pos):
                pos = self.generate_random_position()
            survivor = Survivor(f"Survivor {i + 1}", pos, self)
            self.add_entity(survivor)

        pos = self.generate_random_position()
        while self.is_collision(pos):
            pos = self.generate_random_position()
        self.killer = Killer("Jason", pos, self)  # Pass the Game instance to the Killer constructor
        self.add_entity(self.killer)

    def run(self):
        self.initialize_game()
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.update()
            self.draw()

            clock.tick(30)  # Cap the frame rate at 30 FPS

        pygame.quit()

if __name__ == "__main__":
    game = Game(900, 600)
    game.run()