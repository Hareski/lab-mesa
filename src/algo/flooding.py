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

    def is_cell_blocked(self, cell: Cell) -> bool:
        """
        A cell is blocked if it is a wall or occupied by a drone.
        """
        if self.model.is_wall(cell):
            return True
        return any(isinstance(agent, Drone) for agent in cell.agents)

    def is_cell_agent(self, cell: Cell) -> bool:
        """
        A cell is an agent if it is occupied by a locked drone.
        """
        return bool(cell.agents)


    def get_open_moves(self, cells: list[Cell] | None = None) -> list[Cell]:
        """
        Returns adjacent cells that are neither walls nor occupied by locked drones.
        """
        if cells is None:
            return [
                neighbor
                for neighbor in self.cell.neighborhood
                if not self.is_cell_blocked(neighbor)
            ]
        else:
            return [cell for cell in cells if not self.is_cell_blocked(cell)]

    def step(self) -> None:
        back_dir = self.relative_to_cardinal("BACKWARD")
        backward_cell = self.get_cardinal_neighbor(back_dir)

        left = self.get_cardinal_neighbor(self.relative_to_cardinal("LEFT"))
        front = self.get_cardinal_neighbor(self.relative_to_cardinal("FRONT"))
        right = self.get_cardinal_neighbor(self.relative_to_cardinal("RIGHT"))
        open_moves_forward = self.get_open_moves([cell for cell in [left, front, right]
            if cell is not None])

        if (open_moves_forward and backward_cell is not None and
            self.is_cell_blocked(backward_cell)):
            # Random move
            next_move = self.random.choice(open_moves_forward)
            if next_move == left:
                self.turn_left()
            elif next_move == right:
                self.turn_right()
            self.move_forward()
            return
        return
