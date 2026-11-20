import random
from environment import MazeEnvironment
from shortest_path import find_shortest_path


def _shortest(rows, cols, obstacles):
    return find_shortest_path(MazeEnvironment(rows, cols, list(obstacles)))


def winding_maze(rows=8, cols=8, min_moves=18):
    """Block cells on the current shortest path until it is long enough.
    Returns an obstacle list, always solvable."""
    while True:
        cells = [(r, c) for r in range(rows) for c in range(cols)
                 if (r, c) not in [(0, 0), (rows - 1, cols - 1)]]
        obstacles = set()

        for cell in random.sample(cells, 10):
            if _shortest(rows, cols, obstacles | {cell}) is not None:
                obstacles.add(cell)

        while True:
            path = _shortest(rows, cols, obstacles)
            if len(path) - 1 >= min_moves:
                return list(obstacles)

            options = path[1:-1]
            random.shuffle(options)
            for cell in options:
                if _shortest(rows, cols, obstacles | {cell}) is not None:
                    obstacles.add(cell)
                    break
            else:
                break   # stuck, start again with new random walls