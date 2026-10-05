#import "template.typ": *
#import "@preview/cetz:0.4.2": canvas, draw
#import draw: circle, content, line, mark, rect

#show: conf.with(
  title: [Multi-Agent Models with Mesa],
  subtitle: [SMR — Multi-Robot Systems],
  l: [A. Himeur — 2026],
  r: [INSA Lyon],
)

#intro[
  During this lab session, you will get hands-on experience with Mesa, an open-source Python framework dedicated to multi-agent modeling and simulation.

  You will progressively build different exploration policies for a 2D grid tunnel network:
  1. Single-agent approaches: random walk, then the left-hand rule.
  2. An approach where multiple agents cooperate to quickly explore the entire grid.
  3. An approach where multiple agents cooperate with simple signals to return to the base.
  4. Finally, you will formalize the exploration task for reinforcement learning.

  _*Recommendations:* The use of documentation, forums, and language models is encouraged to guide you with syntax and understanding concepts. However, it is essential that you design, write code, test, and analyze yourselves._
]

#exercice[Getting Started]

The goal of this lab session is to deploy a fleet of autonomous drones as a _Multi-Agent System_ (MAS) to explore an unknown underground tunnel network. The agents operate in a GPS-denied, unmapped environment with no prior knowledge of the layout or their absolute global coordinates. To simplify, we model the tunnel network as a 2D grid in which drones move from cell to cell.

During this session, we will respect the main properties of multi-agent systems:
- Each drone controls its own internal state and independently selects its actions.
- Agents do not have complete, global knowledge of the environment.

#figure(
  canvas(length: 0.6cm, {
    import draw: *
    let rows = (
      "############",
      "#B#      # #",
      "# # # ## # #",
      "# # # ## # #",
      "# # # ##   #",
      "# ### ## # #",
      "#     ## # #",
      "############",
    )
    for (y, row) in rows.enumerate() {
      for (x, ch) in row.split("").enumerate() {
        let a = (x, (rows.len() - 1 - y))
        let b = (x + 1, (rows.len() - y))
        let a_s = (x + 0.15, (rows.len() - 1 - y + 0.15))
        let b_s = (x + 1 - 0.15, (rows.len() - y - 0.15))

        if ch == "B" {
          rect(a, b, fill: rgb("#eef2f7"), stroke: luma(160))
          rect(a_s, b_s, fill: rgb("#3f7f80"), stroke: luma(160))
        } else if ch != " " {
          rect(a, b, fill: rgb("#3d4a5c"), stroke: luma(20))
        } else {
          rect(a, b, fill: rgb("#eef2f7"), stroke: luma(160))
        }
      }
    }
    let dirs = (E: (1, 0), N: (0, 1), W: (-1, 0), S: (0, -1))
    for drone in (
      (cell: (4, 6), dir: "E", color: rgb("#e52713")),
      (cell: (11, 2), dir: "N", color: rgb("#e52713")),
    ) {
      let (cx, cy) = (drone.cell.at(0) + 0.5, drone.cell.at(1) + 0.5)
      let (vx, vy) = dirs.at(drone.dir)
      let (px, py) = (-vy, vx)
      let p = (cx + 0.38 * vx, cy + 0.38 * vy)
      let q = (cx - 0.22 * vx + 0.22 * px, cy - 0.22 * vy + 0.22 * py)
      let r = (cx - 0.22 * vx - 0.22 * px, cy - 0.22 * vy - 0.22 * py)
      draw.line(p, q, r, close: true, fill: drone.color, stroke: 0.4pt + luma(20))
    }
  }),
)

#note[
  The provided skeleton loads the map from a CSV file located in `multi_agent/envs/`. Its first line gives the $(x,y)$ coordinates of the base, and the following lines describe the map read from bottom to top: 0 for a traversable tunnel, 1 for an impassable wall. The base is therefore an ordinary tunnel cell, but the only entry and exit point of the tunnel network.
]

Each agent is a drone occupying a single cell. Each agent has a discrete $(x, y)$ position and an orientation facing _North_, _South_, _East_, or _West_. At each time step, it chooses an action: _turn backward_, _move left_, _move right_, _move forward_, or remain stationary (_stay_). If the agent chooses to move to the left or right, its orientation will change according to the direction of movement. On the illustration and the project visualization, the direction of the drawn triangle indicates the drone's current orientation. Each agent can observe its orientation, as well as its von Neumann neighborhood (or 4-neighborhood for north, south, east, west) states among `Wall`, `Tunnel`, or `Agent`.

#q[
  In the illustration above, identify the base and the drones. Give their respective positions and orientations.
]

#q[
  Give the exact and complete observations of both drones.
]

Clone/retrieve the project skeleton we will be working on from:\
#linkwithicon("https://github.com/hareski/lab-mesa")\
_We recommend forking the repository and working on your own fork._

Launch the visualization according to the instructions in `README.md`.
Observe in the visualization the map, the base, and the drone.

Identify the four fundamental simulation components in the source code:
1. The *model*: manages global state, the grid, and scheduling.
2. The *grid*: discrete spatial structure hosting cells and agents.
3. The *agent*: encapsulates the robot's internal state and its behavioral `step()` method.
4. The *simulation loop*: activation sequence that increments the global clock tick.

#q[
  The `step()` method defines the agent's behavior.
  Explain briefly how the simulation schedules the agents' `step()` methods.
  Are the calls to `step()` sequential or concurrent?
  What happens if an agent attempts to move to a cell already occupied by another agent?
]

#call_teacher[After writing briefly about how the simulation schedules the agents' `step()` methods, call the supervisor, potentially with other peers, to discuss the scheduling strategy and its implications.]

// _Note on scheduling: Sequential execution—calling each agent's `step()` method one after another within a simulation tick—introduces an artificial order of precedence, subtly compromising the fundamental multi-agent principle of true simultaneity and physical concurrency. During this session, as for many multi-agent systems, we adopt this assumption._

#q[Using Mesa's grid methods, how does an agent retrieve the list of its immediate neighboring cells? Complete the method `observation()` in `Agent` to give access to all local observations.]

#exercice[Random Walk]

The agent provided in the skeleton applies a trivial behavior: "do not move".

#q[Implement a first simple "random walk" behavior: at each time step, the drone uniformly/randomly selects an action from turning or moving.]

_Use the random generator provided by Mesa (`random.choice`) rather than standard library `random`: this ensures simulation reproducibility from a seed._

#q[Run the simulation several times on the provided map, and record the average number of steps required to explore all reachable cells.]

#q[
  The provided skeleton provides a method `north_neighbor_is_wall()`. Implement a helper function `left_neighbor_is_wall()` that returns the agent's observation in the agent's relative coordinate system.

  _Make sure not to modify the core model: only implement the relative observation, which can be inferred from the agent's current position, orientation, and the map. For the remainder of the session, you are strongly encouraged to write modular helper functions like this._
]

#q[Propose and implement a simple improvement over the "random walk" behavior without changing the assumptions (i.e., no memory, no "GPS", no prior map knowledge, and no communication between agents). Compare its efficiency with the random walk in terms of number of steps required to explore all reachable cells.]

#call_teacher[Compare your idea with your peers, then present your consolidated solution to the instructor.]

#exercice[The "Left-Hand" Rule]

#note[
  *"Left-hand" rule principle.* The agent constantly chooses to move to the "most" left. In doing so, it maintains contact with the wall on its left side.
]

#q[Write the pseudocode for the algorithm representing this "left-hand" behavior.\
  _Clearly specify the inputs and outputs of the algorithm._]

#q[Implement this policy. Validate its execution on the provided map, then test it on a simple custom "T"-shaped map added by you.]

#q[
  An exploration method is said to be complete if it guarantees visiting all reachable cells in finite time.
  Is the left-hand method a complete exploration method?\
  _Hint: When aiming to prove or disprove a property such as "the algorithm explores all reachable cells", what is usually best to look for first?_
]

#exercice[Exploration by Flooding]

We are now looking for a new multi-agent exploration method. The assumptions remain unchanged: no memory, no GPS, no map, etc. The idea is to shift intelligence from the individual drone to the fleet: multiple agents cooperate to cover all tunnels, and the additional information available to them comes not from an individual memory, but from other drones encountered along their path. We will implement this idea using a true multi-agent approach where all agents share the exact same behavior.

#note[
  *Flooding principle.* The idea is to explore the tunnel by leaving a drone on each cell that has already been explored and should no longer be visited (roughly, dead ends) to prevent exploration loops.
]

#q[
  How do agents spawn at the base? Look in the code to see where this is implemented.
  You will also notice a section of unreachable code (inside an always-false condition). This code will be used later, but for now, can you guess what it will enable?
]

#q[
  Implement the drone flooding method on the grid, assuming you have as many drones available as needed to explore the map.
]

#q[Measure the exploration time (in number of simulation steps) as well as the total number of deployed drones as a function of map parameters.]

#call_teacher[Visualize the behavior of your agents on the `complex` map and verify that it matches expected behavior and is consistent with what your peers observe. Finally, show it to your instructor.]

#exercice[Return to Base]

#q[What is the stopping condition of the simulation? Look in the code to see where this termination is implemented. Then, edit it to terminate only when all drones have returned to the base.]

Once the environment has been explored, for the mission to be accomplished, the drones must return to the base and be removed from the simulation. The agents have neither GPS nor a map enabling them to locate the base. We therefore decide to add (only) a state indicator (a simple light) for each drone, observable by its immediate neighbors.

At each simulation step, a drone can:
- change its light state to `Off`, `Red`, or `Green`;
- move/turn to a neighboring cell;
- do both of the above (in one step);
- or do nothing.

The drones will therefore have three possible light states: `Off` (initial deployment state), `Red`, or `Green`. At each simulation step, drones can choose to move, toggle their light to `Off`, `Red`, `Green`, or do nothing. Once chosen, a light state remains fixed until its next explicit change (no automatic shutoff).

#q[Make the necessary changes to store the light attribute within the Mesa architecture so that an agent can inspect the light status of agents located in neighboring cells. Update the `observation()` method in `Agent` to include the light status.]

#q[
  Test your model by implementing a simple behavior:
  - 1% of the time and at random, the agent toggles its light (to `Off`, `Red`, or `Green`);
  - if an agent observes that its light is `Off` while one of its neighbors has its light `Red`, it turns its light `Red`;
  - in all other cases, the agent follows the previous flooding policy.
]

