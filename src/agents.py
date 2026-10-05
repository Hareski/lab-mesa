from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from mesa.discrete_space import FixedAgent, Grid2DMovingAgent

if TYPE_CHECKING:
    from mesa.discrete_space import Cell

    from src.model import Model

logger = logging.getLogger("agent")


class Base(FixedAgent):
    """
    The base station where drones spawn and return to.
    """

    def __init__(self, model: Model, cell: Cell) -> None:
        super().__init__(model)
        self.model: Model = model
        self.cell: Cell = cell

    def spawner(self) -> None:
        drone_cls = getattr(self.model, "drone_class", Drone)
        drone_cls(self.model, cell=self.cell)

    def step(self) -> None:
        n_current = sum(
            len(agents)
            for agent_class, agents in self.model.agents_by_type.items()
            if issubclass(agent_class, Drone)
        )
        n_target = self.model.n_drones

        if len(self.cell.agents) == 1 and n_current < n_target:
            self.spawner()

        # Remove returning drones that reached the base once return is required
        if getattr(self.model, "require_return", False) and getattr(self.model, "exploration_step", None) is not None:
            for agent in list(self.cell.agents):
                if isinstance(agent, Drone):
                    agent.remove()
        elif False:
            # Section of unreachable code mentioned in the lab assignment.
            for agent in list(self.cell.agents):
                if isinstance(agent, Drone):
                    agent.remove()


class Drone(Grid2DMovingAgent):
    """
    The base class for the drones.
    """

    def __init__(self, model: Model, cell: Cell) -> None:
        super().__init__(model)
        self.model: Model = model
        self.cell: Cell = cell
        self.front: str = "N"
        self.light_red: bool = False

    @property
    def light(self) -> bool:
        return self.light_red

    @light.setter
    def light(self, value: bool) -> None:
        self.light_red = value

    def toggle_light(self) -> None:
        """
        Toggles the drone's light status.
        """
        self.light_red = not self.light_red

    def neighbors_have_light_on(self) -> bool:
        """
        Returns True if any drone in neighboring cells has its light On.
        """
        for neighbor in self.cell.neighborhood:
            for agent in neighbor.agents:
                if isinstance(agent, Drone) and (agent.light_red or getattr(agent, "light", False)):
                    return True
        return False

    def is_wall(self, cell_or_coord: Cell | tuple[int, ...]) -> bool:
        """
        Returns True if the cell or coordinate is a wall, False otherwise.
        """
        return self.model.is_wall(cell_or_coord)

    def get_possible_moves(self) -> list[Cell]:
        """
        Returns a list of accessible adjacent cells (non-walls).
        """
        return [
            neighbor
            for neighbor in self.cell.neighborhood
            if not self.model.is_wall(neighbor)
        ]

    def get_cardinal_neighbor(self, direction: str) -> Cell | None:
        """
        Returns the adjacent cell in cardinal direction (N, S, E, W),
        or None if off-grid boundary.
        """
        delta_map = {
            "NORTH": (0, 1),
            "SOUTH": (0, -1),
            "EAST": (1, 0),
            "WEST": (-1, 0),
            "N": (0, 1),
            "S": (0, -1),
            "E": (1, 0),
            "W": (-1, 0),
        }
        direction_upper = direction.upper()
        delta = delta_map.get(direction_upper)
        if delta is None:
            raise ValueError(
                f"Invalid cardinal direction: {direction}. Expected N, S, E, or W."
            )

        target_coord = (
            self.cell.coordinate[0] + delta[0],
            self.cell.coordinate[1] + delta[1],
        )
        for neighbor in self.cell.neighborhood:
            if neighbor.coordinate == target_coord:
                return neighbor
        return None

    def north_neighbor_is_wall(self) -> bool:
        """
        Returns True if the north neighbor is a wall or boundary, False otherwise.
        """
        north_cell = self.get_cardinal_neighbor("N")
        if north_cell is None:
            return True
        return self.model.is_wall(north_cell)

    def relative_to_cardinal(self, rel_dir: str) -> str:
        """
        Maps an agent-relative direction (LEFT, RIGHT, FORWARD, BACKWARD)
        to a cardinal direction based on self.front.
        """
        mapping = {
            "N": {"LEFT": "W", "RIGHT": "E", "FORWARD": "N", "BACKWARD": "S", "FRONT": "N", "BACK": "S"},
            "S": {"LEFT": "E", "RIGHT": "W", "FORWARD": "S", "BACKWARD": "N", "FRONT": "S", "BACK": "N"},
            "E": {"LEFT": "N", "RIGHT": "S", "FORWARD": "E", "BACKWARD": "W", "FRONT": "E", "BACK": "W"},
            "W": {"LEFT": "S", "RIGHT": "N", "FORWARD": "W", "BACKWARD": "E", "FRONT": "W", "BACK": "E"},
        }
        rel_key = rel_dir.upper()
        if rel_key not in mapping[self.front]:
            raise ValueError(f"Invalid relative direction: {rel_dir}")
        return mapping[self.front][rel_key]

    def left_neighbor_is_wall(self) -> bool:
        """
        Returns True if the cell to the agent's left is a wall or boundary, False otherwise.
        """
        left_dir = self.relative_to_cardinal("LEFT")
        cell = self.get_cardinal_neighbor(left_dir)
        if cell is None:
            return True
        return self.model.is_wall(cell)

    def front_neighbor_is_wall(self) -> bool:
        """
        Returns True if the cell directly in front is a wall or boundary.
        """
        cell = self.get_cardinal_neighbor(self.front)
        if cell is None:
            return True
        return self.model.is_wall(cell)

    def right_neighbor_is_wall(self) -> bool:
        """
        Returns True if the cell to the agent's right is a wall or boundary.
        """
        right_dir = self.relative_to_cardinal("RIGHT")
        cell = self.get_cardinal_neighbor(right_dir)
        if cell is None:
            return True
        return self.model.is_wall(cell)

    def back_neighbor_is_wall(self) -> bool:
        """
        Returns True if the cell directly behind is a wall or boundary.
        """
        back_dir = self.relative_to_cardinal("BACKWARD")
        cell = self.get_cardinal_neighbor(back_dir)
        if cell is None:
            return True
        return self.model.is_wall(cell)

    def left_neighbor_has_drone(self) -> bool:
        """
        Returns True if the cell to the agent's left has a drone, False otherwise.
        """
        left_dir = self.relative_to_cardinal("LEFT")
        cell = self.get_cardinal_neighbor(left_dir)
        if cell is None:
            return False
        return any(isinstance(agent, Drone) for agent in cell.agents)

    def front_neighbor_has_drone(self) -> bool:
        """
        Returns True if the cell directly in front has a drone, False otherwise.
        """
        cell = self.get_cardinal_neighbor(self.front)
        if cell is None:
            return False
        return any(isinstance(agent, Drone) for agent in cell.agents)

    def right_neighbor_has_drone(self) -> bool:
        """
        Returns True if the cell to the agent's right has a drone, False otherwise.
        """
        right_dir = self.relative_to_cardinal("RIGHT")
        cell = self.get_cardinal_neighbor(right_dir)
        if cell is None:
            return False
        return any(isinstance(agent, Drone) for agent in cell.agents)

    def back_neighbor_has_drone(self) -> bool:
        """
        Returns True if the cell directly behind has a drone, False otherwise.
        """
        back_dir = self.relative_to_cardinal("BACKWARD")
        cell = self.get_cardinal_neighbor(back_dir)
        if cell is None:
            return False
        return any(isinstance(agent, Drone) for agent in cell.agents)

    def observation(self) -> dict:
        """
        Returns the observation of the drone.
        """
        return {
            "front": self.front,
            "left_wall": self.left_neighbor_is_wall(),
            "front_wall": self.front_neighbor_is_wall(),
            "right_wall": self.right_neighbor_is_wall(),
            "north_wall": self.north_neighbor_is_wall(),
            "left_agent": self.left_neighbor_has_drone(),
            "front_agent": self.front_neighbor_has_drone(),
            "right_agent": self.right_neighbor_has_drone(),
            "back_agent": self.back_neighbor_has_drone(),
        }

    def change_direction(self, new_direction: str) -> None:
        """
        Changes the direction the drone is facing.
        """
        assert new_direction in ["N", "S", "E", "W"], f"Invalid: {new_direction}"
        self.front = new_direction

    def turn_left(self) -> None:
        """
        Turns 90 degrees counter-clockwise.
        """
        turn_map = {"N": "W", "W": "S", "S": "E", "E": "N"}
        self.front = turn_map[self.front]

    def turn_right(self) -> None:
        """
        Turns 90 degrees clockwise.
        """
        turn_map = {"N": "E", "E": "S", "S": "W", "W": "N"}
        self.front = turn_map[self.front]

    def turn_backward(self) -> None:
        """
        Turns 180 degrees around.
        """
        turn_map = {"N": "S", "S": "N", "E": "W", "W": "E"}
        self.front = turn_map[self.front]

    def change_cell(self, new_cell: Cell) -> None:
        """
        Moves the drone to that cell.
        """
        self.move_to(new_cell)

    def move_forward(self) -> bool:
        """
        Moves the drone one cell forward in the direction it is currently facing.
        Returns True if the movement succeeded, False if blocked by a wall or boundary.
        """
        target = self.get_cardinal_neighbor(self.front)
        if target is not None and not self.model.is_wall(target):
            self.change_cell(target)
            return True
        return False

    def change_cell_and_direction(self, new_cell: Cell) -> None:
        """
        Changes orientation based on movement delta and moves to new cell.
        """
        old_x, old_y = self.cell.coordinate
        new_x, new_y = new_cell.coordinate

        if new_x > old_x:
            self.front = "E"
        elif new_x < old_x:
            self.front = "W"
        elif new_y > old_y:
            self.front = "N"
        elif new_y < old_y:
            self.front = "S"

        self.change_cell(new_cell)

    def step(self) -> None:
        """
        Random walk behavior: uniformly/randomly select an action from turning
        or moving forward (even if the movement is blocked by a wall).
        """
        action = self.model.random.choice(
            ["turn_left", "turn_right", "turn_backward", "move_forward"]
        )
        if action == "turn_left":
            self.turn_left()
        elif action == "turn_right":
            self.turn_right()
        elif action == "turn_backward":
            self.turn_backward()
        if not self.observation()["front_wall"] and         not self.observation()["front_agent"]:
            self.move_forward()
        else:
            pass
        return
