import numpy as np
import random
from Player import Player
from QLearningAgent import QLearningAgent

# Define game environment
class GameEnvironment:
    def __init__(self, map_size, num_survivors):
        self.map_size = map_size
        self.num_survivors = num_survivors
        self.killer = Player()
        self.survivors = [Player() for _ in range(num_survivors)]
        self.state_dim = 2 + 2 * num_survivors  # Killer position + (Survivors positions)
        self.killer_action_dim = 2  # Killer's action dimensions
        self.survivor_action_dim = 2  # Survivor's action dimensions
        self.killer_agent = QLearningAgent(state_dim=self.state_dim, action_dim=self.killer_action_dim)
        self.survivors_agents = [QLearningAgent(state_dim=self.state_dim, action_dim=self.survivor_action_dim) for _ in range(num_survivors)]

    def reset(self):
        self.killer.position = np.array([0, 0])
        for survivor in self.survivors:
            survivor.position = np.array([random.uniform(0, self.map_size), random.uniform(0, self.map_size)])
        return self.get_state()

    def get_state(self):
        survivor_positions = [survivor.position for survivor in self.survivors]
        return np.concatenate((self.killer.position, np.ravel(survivor_positions)))

    def step(self, killer_action, survivor_actions):
        # Killer's turn
        self.killer.move(killer_action)

        # Survivors' turn
        for i, survivor in enumerate(self.survivors):
            survivor.move(survivor_actions[i])

        # Calculate rewards
        reward_killer, reward_survivors = self.calculate_rewards()

        # Check if the game is over
        done = self.check_game_over()

        return self.get_state(), reward_killer, reward_survivors, done

    def calculate_rewards(self):
        # You need to define your own reward function based on the game's rules
        reward_killer = 0
        reward_survivors = [0] * self.num_survivors
        # Example: Killer gets reward for catching survivors
        for survivor in self.survivors:
            if np.linalg.norm(self.killer.position - survivor.position) < 0.5:  # Set a catch radius
                reward_killer += 10
                break  # Assume only one survivor can be caught in one step
        # Example: Survivors get reward for staying alive
        for i, survivor in enumerate(self.survivors):
            if np.linalg.norm(self.killer.position - survivor.position) >= 0.5:
                reward_survivors[i] += 1  # Increment reward for each step survived

        return reward_killer, reward_survivors

    def check_game_over(self):
        # You need to define your own criteria for game over
        # Example: Game is over if all survivors are caught or if the killer reaches a certain position
        if np.all([np.linalg.norm(self.killer.position - survivor.position) < 0.5 for survivor in self.survivors]):
            return True
        # Add more conditions for game over if needed
        return False