import json
import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# One pool file per size. The 8x8 file keeps its original name.
POOL_FILES = {8: "maze_pool.json", 10: "maze_pool_10.json"}

POOLS = {}
for size, filename in POOL_FILES.items():
    if os.path.exists(filename):
        with open(filename) as f:
            POOLS[size] = json.load(f)


@app.get("/api/sizes")
def get_sizes():
    return sorted(POOLS.keys())


@app.get("/api/maze")
def get_maze(size: int = 8):
    if size not in POOLS:
        raise HTTPException(status_code=404, detail="No mazes of that size.")
    return random.choice(POOLS[size])


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")