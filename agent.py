import numpy as np
import random
from config import *

class QLearningAgent:
    def __init__(self, action_space_size=3):
        self.q_table = {} # Dictionary for sparse states: state -> [q_val_0, q_val_1, q_val_2]
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.epsilon = EPSILON_START
        self.action_space_size = action_space_size

    def get_q_values(self, state):
        """Helper to get Q-values for a state, initializing if new."""
        if state not in self.q_table:
            self.q_table[state] = [0.0] * self.action_space_size
        return self.q_table[state]

    def choose_action(self, state): # Epsilon-Greedy
        if random.random() < self.epsilon:
            return random.randint(0, self.action_space_size - 1)
        
        q_values = self.get_q_values(state)
        # Select action with max Q-value; break ties randomly
        max_q = max(q_values)
        best_actions = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state):
        """Updates the Q-table using the Q-Learning update rule."""
        current_q = self.get_q_values(state)[action]
        max_next_q = max(self.get_q_values(next_state))
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q

    def decay_epsilon(self):
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)

    def save_model(self, filename="q_table.npy"):
        np.save(filename, self.q_table)

    def load_model(self, filename="q_table.npy"):
        try:
            self.q_table = np.load(filename, allow_pickle=True).item()
            print(f"Loaded Q-table from {filename}")
        except FileNotFoundError:
            print(f"No saved model found at {filename}, starting fresh.")

