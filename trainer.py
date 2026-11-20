from agent import QLearningAgent
from shortest_path import find_shortest_path


def train(env, episodes=3000, max_steps=None, epsilon_decay=0.998):
    """Train normally and record every training episode whose path to the
    goal is shorter than all earlier ones ("records")."""

    bfs_path = find_shortest_path(env)
    if bfs_path is None:
        raise ValueError("Maze has no solution.")
    bfs_moves = len(bfs_path) - 1

    if max_steps is None:
        max_steps = env.rows * env.cols * 3

    agent = QLearningAgent(env.rows, env.cols, env.actions)
    agent.epsilon_decay = epsilon_decay

    best = None
    records = []

    for episode in range(1, episodes + 1):

        state = env.reset()
        path = [state]
        reached = False

        for _ in range(max_steps):
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.learn(state, action, reward, next_state, done)

            if next_state != state:        # wall bumps are not moves
                path.append(next_state)

            state = next_state
            if done:
                reached = True
                break

        agent.epsilon = max(agent.epsilon_min,
                            agent.epsilon * agent.epsilon_decay)

        if reached:
            moves = len(path) - 1
            if best is None or moves < best:
                best = moves
                records.append({"episode": episode, "moves": moves, "path": path})
                if moves == bfs_moves:
                    break                  # AI has matched the optimum

    return {
        "bfs_moves": bfs_moves,
        "solved": best == bfs_moves,
        "records": records
    }


def pick_rounds(result, ratios=(3.0, 2.0, 1.4)):
    """Choose a handful of records spaced by difficulty:
    first success, then ~3x, ~2x, ~1.4x optimal, then the optimum."""

    bfs = result["bfs_moves"]
    records = result["records"]

    rounds = [records[0]]
    for ratio in ratios:
        for rec in records:
            if rec["moves"] <= ratio * bfs:
                if rec is not rounds[-1]:
                    rounds.append(rec)
                break

    if rounds[-1] is not records[-1]:
        rounds.append(records[-1])

    return rounds