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
