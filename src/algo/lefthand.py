from __future__ import annotations

from src.agents import Drone


class LeftHandDrone(Drone):
    """
    Exercise 3: Left-Hand Rule Drone.
    Maintains contact with the wall on its left side by prioritizing:
    1. Turn LEFT and move forward if left is not a wall.
    2. Move FORWARD if front is not a wall.
    3. Turn RIGHT and move forward if right is not a wall.
    4. Turn BACKWARD and move forward.
    """

    def step(self) -> None:
        if not self.left_neighbor_is_wall():
            self.turn_left()
            self.move_forward()
        elif not self.front_neighbor_is_wall():
            self.move_forward()
        elif not self.right_neighbor_is_wall():
            self.turn_right()
            self.move_forward()
        else:
            self.turn_backward()
            self.move_forward()
