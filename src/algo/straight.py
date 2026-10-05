from __future__ import annotations

from src.agents import Drone


class StraightDrone(Drone):
    """
    Exercise 2 (Improvement): Straight Corridor Drone.
    Maintains direction along straight corridors and only chooses
    at intersections or bends, avoiding turning backward unless trapped in a dead end.
    """

    def step(self) -> None:
        possible_moves = self.get_possible_moves()
        if not possible_moves:
            return

        forward_cell = (
            self.get_cardinal_neighbor(self.front)
            if not self.front_neighbor_is_wall()
            else None
        )
        back_dir = self.relative_to_cardinal("BACKWARD")
        backward_cell = self.get_cardinal_neighbor(back_dir)

        # In an intersection (3 or more open exits), choose among non-backward paths
        if len(possible_moves) >= 3:
            non_back = [c for c in possible_moves if c != backward_cell]
            target = (
                self.model.random.choice(non_back)
                if non_back
                else self.model.random.choice(possible_moves)
            )
            self.change_cell_and_direction(target)
            return

        # In a corridor, prioritize continuing straight forward
        if forward_cell is not None:
            self.change_cell_and_direction(forward_cell)
            return

        # At a bend or junction without forward option, avoid going backward if possible
        non_back = [c for c in possible_moves if c != backward_cell]
        if non_back:
            target = self.model.random.choice(non_back)
        else:
            target = backward_cell if backward_cell is not None else possible_moves[0]

        self.change_cell_and_direction(target)
