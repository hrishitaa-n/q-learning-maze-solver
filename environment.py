import numpy as np


class MazeEnvironment:

    def __init__(self, rows=5, cols=5, obstacles=None):

        self.rows = rows
        self.cols = cols

        self.start = (0, 0)
        self.goal = (rows - 1, cols - 1)

        # Default obstacles = your original 5x5 maze
        if obstacles is None:
            obstacles = [
                (1, 1),
                (1, 3),
                (3, 0),
                (3, 1),
                (3, 4)
            ]

        # Convert every obstacle to a tuple. JSON gives us lists like
        # [1, 1], and in Python [1, 1] != (1, 1), so the obstacle
        # checks below would silently fail without this line.
        self.obstacles = [tuple(obstacle) for obstacle in obstacles]

        # Safety checks
        if self.start in self.obstacles or self.goal in self.obstacles:
            raise ValueError("Start and goal cannot be obstacles.")

        for (r, c) in self.obstacles:
            if not (0 <= r < rows and 0 <= c < cols):
                raise ValueError(f"Obstacle {(r, c)} is outside the grid.")

        self.actions = {
            0: (-1, 0),  # Up
            1: (1, 0),   # Down
            2: (0, -1),  # Left
            3: (0, 1)    # Right
        }

        self.reset()

    def reset(self):
        self.position = self.start
        return self.position

    def step(self, action):

        row, col = self.position

        move_row, move_col = self.actions[action]

        new_row = row + move_row
        new_col = col + move_col

        # Check grid boundaries
        if not (0 <= new_row < self.rows and
                0 <= new_col < self.cols):
            return self.position, -10, False

        new_position = (new_row, new_col)

        # Check obstacles
        if new_position in self.obstacles:
            return self.position, -10, False

        self.position = new_position

        # Check goal
        if self.position == self.goal:
            return self.position, 100, True

        return self.position, -1, False

    def display(self):

        maze = np.zeros((self.rows, self.cols), dtype=str)
        maze[:] = "."

        for obstacle in self.obstacles:
            maze[obstacle] = "X"

        maze[self.start] = "S"
        maze[self.goal] = "G"
        maze[self.position] = "A"

        print(maze)