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

        if False:
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

    def observation(self) -> dict:
        """
        Returns the observation of the drone.
        """
        raise NotImplementedError("To be implemented.")

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

    def step(self) -> None:
        """
        The function to specify the agent's behavior.
        The default skeleton applies a trivial behavior: "do not move".
        """
        pass
