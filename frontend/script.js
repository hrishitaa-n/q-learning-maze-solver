const ROUNDS_PER_GAME = 3;

const SIZES = [8, 10];     // add 12 here later if you build a 12x12 pool
const pools = {};          // pool files, downloaded once per size
const seenIds = {};        // mazes already shown this session, per size

let maze = null;
let currentSize = 8;       // the maze size the player picked
let aiRounds = [];         // the 3 AI stages used in this game
let player = [0, 0];
let moves = 0;
let finished = false;
let roundIndex = 0;        // 0 means Round 1
let counterTimer = null;

// Replay state
let replayTimer = null;
let replaying = false;     // true while the AI replay is on screen
let aiPos = null;          // where the AI robot is right now
let aiTrail = [];          // cells the AI has visited so far

const KEYS = {
  ArrowUp:    [-1, 0],
  ArrowDown:  [1, 0],
  ArrowLeft:  [0, -1],
  ArrowRight: [0, 1],
};

// Presentation-only commentary. It observes the existing game messages and
// never participates in movement, scoring, timers, or round progression.
const flavor = document.getElementById("flavor");
function setFlavor(message) {
  if (flavor.textContent !== message) flavor.textContent = message;
}
function updateFlavor() {
  const result = document.getElementById("result").textContent;
  const counter = document.getElementById("counter").textContent;
  const replay = document.getElementById("replayInfo").textContent;
  const round = document.getElementById("round").textContent;

  if (replay.startsWith("AI move")) {
    setFlavor("The AI has a plan. Hopefully.");
  } else if (replay.startsWith("The AI reached")) {
    setFlavor("Fine. The robot has officially flexed.");
  } else if (counter.includes("Humans Win")) {
    setFlavor("OKAY, SHOW OFF! You actually did it.");
  } else if (counter.includes("AI takes over")) {
    setFlavor("Well... that was an interesting strategy.");
  } else if (counter.includes("The AI trained")) {
    setFlavor("Well... that was an interesting strategy.");
  } else if (counter.includes("You beat an AI")) {
    setFlavor("Not bad. But the maze is still being extremely specific.");
  } else if (round.startsWith("Round 2")) {
    setFlavor("Round two. Let's see if you've learned anything.");
  } else if (round.startsWith("Round 3")) {
    setFlavor("Final round. The drama is entirely unnecessary.");
  } else if (document.getElementById("info").textContent.startsWith("Goal:")) {
    setFlavor("Fresh maze. Fresh opportunities to embarrass yourself.");
  }
}

new MutationObserver(updateFlavor).observe(document.querySelector(".game-frame"), {
  childList: true,
  characterData: true,
  subtree: true
});

// ---------- maze pool (loaded from static JSON files) ----------

async function getPool(size) {
  if (!pools[size]) {
    const response = await fetch("data/pool_" + size + ".json");
    pools[size] = await response.json();
    seenIds[size] = new Set();
  }
  return pools[size];
}

// Random maze that the player hasn't seen yet this session
async function pickMaze(size) {
  const pool = await getPool(size);
  let fresh = pool.filter(m => !seenIds[size].has(m.id));
  if (fresh.length === 0) {          // seen them all, start over
    seenIds[size].clear();
    fresh = pool;
  }
  const chosen = fresh[Math.floor(Math.random() * fresh.length)];
  seenIds[size].add(chosen.id);
  return chosen;
}

// ---------- drawing ----------

function isSame(a, b) {
  return a[0] === b[0] && a[1] === b[1];
}

function isWall(pos) {
  return maze.obstacles.some(o => isSame(o, pos));
}

function drawMaze() {
  const grid = document.getElementById("maze");
  grid.innerHTML = "";

  // 50px cells for small grids, smaller cells so big grids still fit
  const available = Math.min(window.innerWidth - 40, 760);   // total grid width allowed
const size = Math.min(80, Math.floor(available / maze.cols));
  grid.style.gridTemplateColumns = `repeat(${maze.cols}, ${size}px)`;

  const start = [0, 0];
  const goal = [maze.rows - 1, maze.cols - 1];

  for (let row = 0; row < maze.rows; row++) {
    for (let col = 0; col < maze.cols; col++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.style.width = size + "px";
      cell.style.height = size + "px";
      cell.style.fontSize = Math.floor(size * 0.55) + "px";
      const pos = [row, col];

      const isStart = isSame(pos, start);
      const isGoal = isSame(pos, goal);

      if (isStart) cell.classList.add("start");
      if (isGoal) cell.classList.add("goal");
      if (isWall(pos)) cell.classList.add("obstacle");

      // Light-blue trail where the AI has been (replay only)
      if (!isStart && !isGoal && aiTrail.some(t => isSame(t, pos))) {
        cell.classList.add("trail");
      }

      if (aiPos && isSame(pos, aiPos)) {
        cell.classList.add("ai-cell");
        cell.textContent = "🤖";                       // the AI
      } else if (!replaying && isSame(pos, player)) {
        cell.classList.add("player-cell");
        const face = document.createElement("img");    // you
        face.src = "images/me.jpg";
        face.alt = "You";
        face.className = "face";
        cell.appendChild(face);
      } else if (isGoal) {
        const job = document.createElement("span");    // the prize
        job.className = "job";
        job.textContent = "JOB";
        job.style.fontSize = Math.floor(size * 0.36) + "px";
        cell.appendChild(job);
      } else if (isWall(pos)) {
        cell.textContent = "💤";                       // sleeping walls
      }
      grid.appendChild(cell);
    }
  }
}
function showNextButton(show) {
  const button = document.getElementById("nextRound");
  button.hidden = !show;
  button.textContent = "Round " + (roundIndex + 2);
}

function showWatchButton(show) {
  const button = document.getElementById("watchAI");
  button.hidden = !show;
  button.disabled = false;
  button.textContent = "See what the AI did";
}

// Counts up from 0 to `target`, then calls onDone
function animateCounter(target, onDone) {
  const el = document.getElementById("counter");
  clearInterval(counterTimer);
  let shown = 0;
  const step = Math.max(1, Math.ceil(target / 50));

  counterTimer = setInterval(() => {
    shown = Math.min(target, shown + step);
    el.textContent = "AI is learning... episode " + shown;
    if (shown >= target) {
      clearInterval(counterTimer);
      onDone();
    }
  }, 30);
}

// ---------- AI replay ----------

function stopReplay() {
  clearInterval(replayTimer);
  replaying = false;
  aiPos = null;
  aiTrail = [];
  document.getElementById("replayInfo").textContent = "";
}

function startReplay() {
  const ai = aiRounds[roundIndex];
  const path = ai.path;
  const button = document.getElementById("watchAI");
  const info = document.getElementById("replayInfo");

  stopReplay();
  replaying = true;
  button.disabled = true;

  // Long paths play a bit faster so the replay never drags
  const delay = Math.max(50, Math.min(250, Math.floor(6000 / path.length)));
  let i = 0;

  replayTimer = setInterval(() => {
    aiPos = path[i];
    aiTrail = path.slice(0, i + 1);
    info.textContent = "AI move " + i + " of " + (path.length - 1);
    drawMaze();
    i++;

    if (i >= path.length) {
      clearInterval(replayTimer);
      info.textContent = "The AI reached the goal in " + ai.moves +
        " moves (after " + ai.episode + " episodes of training).";
      button.disabled = false;
      button.textContent = "Watch again";
    }
  }, delay);
}

// ---------- game rules ----------

function finishAttempt() {
  finished = true;
  const ai = aiRounds[roundIndex];
  const last = aiRounds[aiRounds.length - 1];
  const isLastRound = roundIndex === aiRounds.length - 1;
  const result = document.getElementById("result");
  const counter = document.getElementById("counter");

  result.textContent = "You: " + moves + " moves. AI: " + ai.moves + " moves.";

  // Only the shortest route wins the game
  if (moves === maze.bfs_moves) {
    animateCounter(last.episode, () => {
      counter.textContent = "🏆 Humans Win! You found the shortest route (" +
        maze.bfs_moves + " moves). The AI needed " + last.episode +
        " episodes of training to match you.";
      showNextButton(false);
      showWatchButton(false);
    });
    return;
  }

  // Anything else loses the round
  animateCounter(ai.episode, () => {
    if (isLastRound) {
      counter.textContent = "🤖 AI takes over! After " + ai.episode +
        " episodes it knows the shortest route (" + ai.moves + " moves).";
      showNextButton(false);
    } else {
      counter.textContent = moves > ai.moves
        ? "The AI trained for " + ai.episode + " episodes and beat you."
        : "You beat an AI that trained for " + ai.episode +
          " episodes, but the shortest route is " + maze.bfs_moves + " moves.";
      showNextButton(true);
    }
    showWatchButton(true);
  });
}

function movePlayer(dRow, dCol) {
  if (finished) return;

  const newPos = [player[0] + dRow, player[1] + dCol];

  // Border or wall: nothing happens and it does NOT count as a move
  if (newPos[0] < 0 || newPos[0] >= maze.rows ||
      newPos[1] < 0 || newPos[1] >= maze.cols) return;
  if (isWall(newPos)) return;

  player = newPos;
  moves++;
  document.getElementById("moves").textContent = "Moves: " + moves;
  drawMaze();

  if (isSame(player, [maze.rows - 1, maze.cols - 1])) {
    finishAttempt();
  }
}

// Start a fresh attempt on the same maze, at the current round
function resetAttempt() {
  clearInterval(counterTimer);
  stopReplay();
  player = [0, 0];
  moves = 0;
  finished = false;
  document.getElementById("moves").textContent = "Moves: 0";
  document.getElementById("result").textContent = "";
  document.getElementById("counter").textContent = "";
  document.getElementById("round").textContent =
    "Round " + (roundIndex + 1) + " of " + aiRounds.length;
  showNextButton(false);
  showWatchButton(false);
  drawMaze();
}

async function loadMaze() {
  clearInterval(counterTimer);
  stopReplay();

  maze = await pickMaze(currentSize);

  // The last 3 saved stages: third-last, second-last, last (optimal)
  aiRounds = maze.rounds.slice(-ROUNDS_PER_GAME);
  roundIndex = 0;

  document.getElementById("info").textContent =
    "Goal: Get the job in exactly " + maze.bfs_moves +
    " moves, the shortest possible route. You get " + aiRounds.length + " rounds.";
  resetAttempt();
}

// Fill the dropdown with the available maze sizes
async function loadSizes() {
  const sizes = SIZES;

  const select = document.getElementById("size");
  select.innerHTML = "";
  for (const s of sizes) {
    const option = document.createElement("option");
    option.value = s;
    option.textContent = s + " × " + s;
    select.appendChild(option);
  }

  if (!sizes.includes(currentSize)) currentSize = sizes[0];
  select.value = currentSize;
}

// ---------- events ----------

document.addEventListener("keydown", (event) => {
  if (KEYS[event.key]) {
    event.preventDefault();
    movePlayer(KEYS[event.key][0], KEYS[event.key][1]);
  }
});

document.getElementById("size").addEventListener("change", (event) => {
  currentSize = Number(event.target.value);
  event.target.blur();       // so arrow keys move the robot, not the dropdown
  loadMaze();
});
document.getElementById("newMaze").addEventListener("click", loadMaze);
document.getElementById("watchAI").addEventListener("click", (event) => {
  event.target.blur();
  startReplay();
});
document.getElementById("nextRound").addEventListener("click", () => {
  roundIndex++;
  resetAttempt();
});

async function start() {
  await loadSizes();
  await loadMaze();
}
start();
