from environment import MazeEnvironment
from shortest_path import find_shortest_path

env = MazeEnvironment(rows=8, cols=8, obstacles=[[1, 1], [2, 2], [3, 5], [5, 3]])
env.display()
path = find_shortest_path(env)
print("Shortest moves:", len(path) - 1)