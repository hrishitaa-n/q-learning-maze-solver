import json
import random
import sys
import time
from collections import Counter
from environment import MazeEnvironment
from maze_generator import winding_maze
from trainer import train, pick_rounds

# ---------- settings (the only part you may want to change) ----------
ROWS, COLS = 10, 10
TARGET_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 300
MIN_ROUNDS = 4
PATH_TARGETS = (22, 30)      # shortest possible route on 10x10 is 18 moves
EPISODES = 6000              # untested guess, the pilot run checks it
EPSILON_DECAY = 0.999        # untested guess, explores longer than 8x8
OUTPUT_FILE = "maze_pool_10.json"
# ---------------------------------------------------------------------

pool = []
seen = set()
tried = 0
unsolved = 0
too_few_rounds = 0
started = time.time()

try:
    while len(pool) < TARGET_SIZE:
        tried += 1

        obstacles = winding_maze(ROWS, COLS, random.randint(*PATH_TARGETS))

        layout = frozenset(obstacles)
        if layout in seen:
            continue
        seen.add(layout)

        env = MazeEnvironment(ROWS, COLS, obstacles)
        result = train(env, episodes=EPISODES, epsilon_decay=EPSILON_DECAY)

        if not result["solved"]:
            unsolved += 1
            continue

        rounds = pick_rounds(result)
        if len(rounds) < MIN_ROUNDS:
            too_few_rounds += 1
            continue

        pool.append({
            "id": len(pool) + 1,
            "rows": ROWS,
            "cols": COLS,
            "obstacles": sorted(obstacles),
            "bfs_moves": result["bfs_moves"],
            "rounds": rounds,
        })

        if len(pool) % 10 == 0:
            minutes = (time.time() - started) / 60
            print(f"{len(pool)} / {TARGET_SIZE} saved  ({minutes:.1f} min)")

except KeyboardInterrupt:
    print("\nStopped early. Saving what we have so far...")

with open(OUTPUT_FILE, "w") as f:
    json.dump(pool, f)

minutes = (time.time() - started) / 60
print(f"\nDone in {minutes:.1f} min. Generated: {tried} | saved: {len(pool)}")
print(f"Discarded: AI never reached optimum = {unsolved}, "
      f"too few rounds = {too_few_rounds}")
print("BFS lengths:", sorted(Counter(m["bfs_moves"] for m in pool).items()))
print("Rounds per maze:", sorted(Counter(len(m["rounds"]) for m in pool).items()))