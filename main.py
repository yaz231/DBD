# Import necessary classes and functions from game.py
from GameEnvironment import GameEnvironment

# Import RL-related classes and functions
from QLearningAgent import QLearningAgent
from Player import Player
import pygame
from tqdm import tqdm

import numpy as np

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class GameVisualizer:
    def __init__(self, map_size, num_survivors):
        self.map_size = map_size
        self.num_survivors = num_survivors
        self.screen_size = 600
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption("Survivors and Killer")

    def draw_environment(self, state):
        self.screen.fill((255, 255, 255))  # Fill the screen with white color

        # Draw killer
        killer_x, killer_y = state[0], state[1]
        pygame.draw.circle(self.screen, (255, 0, 0), (int(killer_x * self.screen_size / self.map_size), int(killer_y * self.screen_size / self.map_size)), 10)

        # Draw survivors
        positions = state[2:]
        survivors_pos = [(positions[i], positions[i + 1]) for i in range(0, len(positions), 2)]
        for pos in survivors_pos:
            survivor_x, survivor_y = pos
            pygame.draw.circle(self.screen, (0, 255, 0), (int(survivor_x * self.screen_size / self.map_size), int(survivor_y * self.screen_size / self.map_size)), 10)

        pygame.display.flip()  # Update the display


def main():
    # Initialize the game environment
    map_size = 10
    num_survivors = 5
    env = GameEnvironment(map_size, num_survivors)

    # Initialize the visualizer
    visualizer = GameVisualizer(map_size, num_survivors)

    # Initialize the RL agents
    state_dim = 2 + 2 * num_survivors  # Killer position + (Survivors positions)

    # Create Q-learning agents
    agents = [QLearningAgent(state_dim, 2) for _ in range(num_survivors + 1)]

    # Train RL agents
    num_episodes = 100
    for episode in tqdm(range(num_episodes)):
        state = env.reset()
        done = False
        total_reward = 0
        step_counter = 0
        while not done and step_counter < 100:
            # Choose action based on the current state
            actions = [agents[i].choose_action(state) for i in range(num_survivors + 1)]

            # Take action and observe the next state and reward
            next_state, reward_killer, reward_survivors, done = env.step(actions[0], actions[1:])

            # Update Q-values based on the observed transition
            agents[0].update_q_table(state, actions[0], reward_killer, next_state)
            for i in range(num_survivors):
                agents[i + 1].update_q_table(state, actions[i + 1], reward_survivors[i], next_state)

            # Transition to the next state
            state = next_state
            total_reward += sum([reward_killer] + reward_survivors)

            # Visualize the environment
            visualizer.draw_environment(state)

            step_counter += 1

        tqdm.write(f"Episode {episode + 1}, Total Reward: {total_reward}")

    # Test RL agents after training
    state = env.reset()
    done = False
    while not done:
        # Choose action based on the current state
        actions = [agents[i].choose_action(state) for i in range(num_survivors + 1)]

        # Take action and observe the next state and reward
        next_state, reward_killer, reward_survivors, done = env.step(actions[0], actions[1:])

        # Transition to the next state
        state = next_state

        # Visualize the environment
        visualizer.draw_environment(state)

        # Print action, reward, and whether the episode is done
        print(f"Action: {actions}, Reward (Killer): {reward_killer}, Reward (Survivors): {reward_survivors}, Done: {done}")

if __name__ == "__main__":
    main()