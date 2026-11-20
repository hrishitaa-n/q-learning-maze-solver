import json
import random
from collections import Counter
from environment import MazeEnvironment
from maze_generator import winding_maze
from trainer import train, pick_rounds

ROWS, COLS = 8, 8
TARGET_SIZE = 300      # how many mazes to keep
MIN_ROUNDS = 4         # a maze needs at least this many rounds

pool = []
seen = set()           # remembers obstacle layouts so we never save duplicates
tried = 0

while len(pool) < TARGET_SIZE:
    tried += 1

    min_moves = random.randint(18, 26)
    obstacles = winding_maze(ROWS, COLS, min_moves)

    layout = frozenset(obstacles)
    if layout in seen:
        continue
    seen.add(layout)

    env = MazeEnvironment(ROWS, COLS, obstacles)
    result = train(env)

    if not result["solved"]:
        continue                      # AI never reached the optimum, discard

    rounds = pick_rounds(result)
    if len(rounds) < MIN_ROUNDS:
        continue                      # not enough rounds, discard

    pool.append({
        "id": len(pool) + 1,
        "rows": ROWS,
        "cols": COLS,
        "obstacles": sorted(obstacles),
        "bfs_moves": result["bfs_moves"],
        "rounds": rounds,
    })

    if len(pool) % 25 == 0:
        print(f"{len(pool)} / {TARGET_SIZE} mazes saved...")

with open("maze_pool.json", "w") as f:
    json.dump(pool, f)

print("\nDone. Mazes generated:", tried, "| saved:", len(pool))
print("BFS lengths:", sorted(Counter(m["bfs_moves"] for m in pool).items()))
print("Rounds per maze:", sorted(Counter(len(m["rounds"]) for m in pool).items()))