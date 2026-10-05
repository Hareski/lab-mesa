# Multi-Agent Tunnel Exploration with Mesa

Multi-Agent Systems (MAS) simulation framework for autonomous tunnel network exploration using [Mesa 3.x](https://github.com/projectmesa/mesa) and [Solara](https://solara.dev/).

```
lab-mesa/
├── src/                    # Skeleton package (for students)
│   ├── agents.py           # Drone and Base (spawner/base station)
│   ├── model.py            # Simulation Model and grid initialization
│   ├── rendering.py        # Custom canvas visualization
│   ├── app.py              # Interactive Solara application
│   └── maps/               # Map CSV files
├── tests/                  # Unit tests for the skeleton
└── pyproject.toml          # Project configuration
```

## Quick Start

Requires Python 3.11 or newer.

---

## Skeleton Structure

The skeleton contains base agent and model definitions:
- Drone action primitives (`turn_left()`, `turn_right()`, `turn_backward()`, `move_forward()`, `stay`) and helpers (`is_wall()`, `north_neighbor_is_wall()`) are provided.
- `Base` agent manages drone deployment at the starting cell.
- Drone observations (`observation()`, `left_neighbor_is_wall()`) and exploration policies are left for the student to implement.
- `Drone.step()` defaults to "do not move".

### Run Visualization

```bash
solara run src/app.py
```

### Run Tests

```bash
pytest
```

---

## Map File Format

CSV files under `src/maps/` describe the tunnel network. Row 0 holds the
start cell as `start_x,start_y` (y measured from the top row of the map);
every subsequent row is a map row read top-to-bottom, where `1` = wall and
`0` = tunnel.

### Map constraints

To make the policies well-behaved:

- The tunnel network must be a **tree**: corridors never form loops, so any
  front/left/right search has an unambiguous continuation except at junctions.
- **Corridors are at most one cell wide.** No 2x2 (or larger) open blocks;
  each tunnel cell has at most one open neighbor per row/column.
- Every tunnel row/column forms a single straight segment joining exactly two
  junction/endpoint cells; junctions (cells with >= 3 open neighbors) are the
  only branching points.
- Endpoints (dead ends) are enclosed by walls on three sides.

`conftest.py`'s small map follows the same format (16x19, 36 tunnel cells,
start at (1, 9)).
