import json
from environment import MazeEnvironment
from shortest_path import find_shortest_path
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "maze_pool.json"
with open(filename) as f:

    pool = json.load(f)

problems = 0


def check(condition, maze_id, message):
    global problems
    if not condition:
        problems += 1
        print(f"Maze {maze_id}: {message}")


for maze in pool:
    mid = maze["id"]
    rows, cols = maze["rows"], maze["cols"]
    obstacles = {tuple(o) for o in maze["obstacles"]}
    start, goal = (0, 0), (rows - 1, cols - 1)
    rounds = maze["rounds"]

    # BFS, recomputed from scratch, must agree with the saved number
    env = MazeEnvironment(rows, cols, maze["obstacles"])
    check(len(find_shortest_path(env)) - 1 == maze["bfs_moves"], mid, "BFS mismatch")

    for n, r in enumerate(rounds, 1):
        path = [tuple(p) for p in r["path"]]
        check(path[0] == start, mid, f"round {n} does not start at S")
        check(path[-1] == goal, mid, f"round {n} does not end at G")
        check(len(path) - 1 == r["moves"], mid, f"round {n} move count mismatch")
        for a, b in zip(path, path[1:]):
            check(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, mid, f"round {n} jumps")
            check(b not in obstacles, mid, f"round {n} walks through a wall")
            check(0 <= b[0] < rows and 0 <= b[1] < cols, mid, f"round {n} leaves grid")

    moves = [r["moves"] for r in rounds]
    check(moves == sorted(moves, reverse=True) and len(set(moves)) == len(moves),
          mid, "rounds do not strictly improve")
    check(moves[-1] == maze["bfs_moves"], mid, "last round is not optimal")
    episodes = [r["episode"] for r in rounds]
    check(episodes == sorted(episodes), mid, "episodes out of order")

layouts = {frozenset(tuple(o) for o in m["obstacles"]) for m in pool}
check(len(layouts) == len(pool), "pool", "duplicate layouts")

print("Mazes checked:", len(pool), "| problems found:", problems)