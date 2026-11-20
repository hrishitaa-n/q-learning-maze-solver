
import numpy as np
import random


class QLearningAgent:

    def __init__(self, rows, cols, actions):

        self.rows = rows
        self.cols = cols
        self.actions = actions

        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

        self.q_table = np.zeros((rows * cols, len(actions)))

    def choose_action(self, state):

        row, col = state
        state_index = row * self.cols + col

        if random.random() < self.epsilon:
            return random.choice(list(self.actions.keys()))

        return int(np.argmax(self.q_table[state_index]))

    def learn(self, state, action, reward, next_state, done):

        row, col = state
        state_index = row * self.cols + col

        next_row, next_col = next_state
        next_state_index = next_row * self.cols + next_col

        old_value = self.q_table[state_index, action]
        future_value = np.max(self.q_table[next_state_index])

        if done:
            target = reward
        else:
            target = reward + self.gamma * future_value

        self.q_table[state_index, action] = (
            old_value + self.alpha * (target - old_value)
        )
