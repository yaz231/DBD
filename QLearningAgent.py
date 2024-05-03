import numpy as np
import torch
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
class QLearningAgent:
    def __init__(self, state_dim, action_dim, discount_factor=0.99):
        self.discount_factor = discount_factor
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.q_network = self._build_model()

    def _build_model(self):
        model = Sequential([
            Dense(64, activation='relu', input_shape=(self.state_dim,)),
            Dense(64, activation='relu'),
            Dense(self.action_dim)  # Output layer size should be sum of all action dimensions
        ])
        model.compile(loss='mse', optimizer=Adam(learning_rate=0.1))
        return model

    def choose_action(self, state):
        state = np.array(state).reshape(1, -1)
        q_values = self.q_network.predict(state)[0]
        return np.argmax(q_values)

    def update_q_table(self, state, action, reward, next_state):
        state = np.array(state).reshape(1, -1)
        next_state = np.array(next_state).reshape(1, -1)
        target = reward + self.discount_factor * np.max(self.q_network.predict(next_state))
        target_full = self.q_network.predict(state)
        target_full[0][action] = target
        self.q_network.fit(state, target_full, epochs=1, verbose=0)