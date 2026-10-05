from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents import Drone

if TYPE_CHECKING:
    from mesa.discrete_space import Cell


class FloodingDrone(Drone):
    """
    Exercise 4: Exploration by Flooding.
    Agents explore the tunnel network and lock themselves in dead ends
    or explored endpoints to prevent loops and direct subsequent drones
    into unexplored branches.
    """

    def __init__(self, model, cell: Cell) -> None:
        super().__init__(model, cell)
        self.stopped: bool = False

    def is_cell_blocked(self, cell: Cell) -> bool:
        """
        A cell is blocked if it is a wall or occupied by a locked drone.
        """
        if self.model.is_wall(cell):
            return True
        for agent in cell.agents:
            if isinstance(agent, FloodingDrone) and agent.stopped:
                return True
        return False

    def get_open_moves(self) -> list[Cell]:
        """
        Returns adjacent cells that are neither walls nor occupied by locked drones.
        """
        return [
            neighbor
            for neighbor in self.cell.neighborhood
            if not self.is_cell_blocked(neighbor)
        ]

    def step(self) -> None:
        if self.stopped:
            return

        open_moves = self.get_open_moves()
        back_dir = self.relative_to_cardinal("BACKWARD")
        backward_cell = self.get_cardinal_neighbor(back_dir)
        non_back = [c for c in open_moves if c != backward_cell]

        if not non_back:
            # Reached a dead end or sealed branch: lock in place
            self.stopped = True
            return

        # Prioritize unexplored cells
        unexplored = [
            c
            for c in non_back
            if self.model.explored_cells[c.coordinate[1], c.coordinate[0]] == 0
        ]
        if unexplored:
            next_cell = self.model.random.choice(unexplored)
        else:
            forward = self.get_cardinal_neighbor(self.front)
            if forward is not None and forward in non_back:
                next_cell = forward
            else:
                next_cell = self.model.random.choice(non_back)

        self.change_cell_and_direction(next_cell)
