
from collections import deque


def find_shortest_path(env):

    queue = deque([[env.start]])
    visited = {env.start}

    while queue:

        path = queue.popleft()
        current = path[-1]

        if current == env.goal:
            return path

        for move in env.actions.values():

            row = current[0] + move[0]
            col = current[1] + move[1]

            next_position = (row, col)

            if not (0 <= row < env.rows and 0 <= col < env.cols):
                continue

            if next_position in env.obstacles:
                continue

            if next_position in visited:
                continue

            visited.add(next_position)
            queue.append(path + [next_position])

    return None
