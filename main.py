
from environment import MazeEnvironment
from agent import QLearningAgent
from shortest_path import find_shortest_path


# ==========================================
# 1. CREATE THE MAZE
# ==========================================

env = MazeEnvironment()

# Calculate shortest path using BFS
shortest_path = find_shortest_path(env)
shortest_moves = len(shortest_path) - 1

print("Shortest possible path:", shortest_path)
print("Shortest possible moves:", shortest_moves)


# ==========================================
# 2. CREATE THE LEARNING AGENT
# ==========================================

agent = QLearningAgent(
    env.rows,
    env.cols,
    env.actions
)

print("\nAgent created successfully!")
print("Q-table shape:", agent.q_table.shape)


# ==========================================
# 3. TRAIN THE AGENT
# ==========================================

episodes = 2000
max_steps = 100

successful_episodes = 0
total_successful_steps = 0

print("\nTraining started...")

for episode in range(episodes):

    state = env.reset()

    for step in range(max_steps):

        # Agent chooses an action
        action = agent.choose_action(state)

        # Environment responds
        next_state, reward, done = env.step(action)

        # Agent updates its Q-table
        agent.learn(state, action, reward, next_state, done)

        # Move to the next state
        state = next_state

        # Check whether goal was reached
        if done:
            successful_episodes += 1
            total_successful_steps += step + 1
            break

    # Reduce exploration after each episode
    agent.epsilon = max(
        agent.epsilon_min,
        agent.epsilon * agent.epsilon_decay
    )


# ==========================================
# 4. TRAINING RESULTS
# ==========================================

print("\n========== TRAINING RESULTS ==========")

success_rate = (successful_episodes / episodes) * 100

print("Total episodes:", episodes)
print("Successful episodes:", successful_episodes)
print("Success rate:", round(success_rate, 2), "%")

if successful_episodes > 0:
    average_steps = total_successful_steps / successful_episodes
    print("Average steps:", round(average_steps, 2))

print("Final epsilon:", agent.epsilon)


# ==========================================
# 5. EVALUATE THE TRAINED AGENT
# ==========================================

print("\n========== EVALUATION (100 TESTS) ==========")

test_episodes = 100

test_successes = 0
optimal_paths = 0
total_test_steps = 0

# Disable random exploration
agent.epsilon = 0

for episode in range(test_episodes):

    state = env.reset()
    done = False
    steps_taken = 0

    for step in range(max_steps):

        # Choose the best learned action
        action = agent.choose_action(state)

        # Execute action
        next_state, reward, done = env.step(action)

        state = next_state
        steps_taken += 1

        if done:
            break

    # Record successful test
    if done:
        test_successes += 1
        total_test_steps += steps_taken

        # Check whether the route was shortest
        if steps_taken == shortest_moves:
            optimal_paths += 1


# ==========================================
# 6. EVALUATION RESULTS
# ==========================================

test_success_rate = (test_successes / test_episodes) * 100

print("\n========== FINAL EVALUATION RESULTS ==========")

print("Total test episodes:", test_episodes)
print("Successful tests:", test_successes)
print("Failed tests:", test_episodes - test_successes)

print("Test success rate:", round(test_success_rate, 2), "%")

if test_successes > 0:

    average_test_steps = total_test_steps / test_successes

    optimal_path_rate = (optimal_paths / test_successes) * 100

    print("Average steps:", round(average_test_steps, 2))
    print("Optimal paths:", optimal_paths)
    print("Optimal path rate:", round(optimal_path_rate, 2), "%")

else:
    print("No successful test episodes.")

print("\nEvaluation completed!")
