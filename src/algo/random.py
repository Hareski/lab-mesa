from __future__ import annotations

from src.agents import Drone


class RandomDrone(Drone):
    """
    Random Walk Drone.
    Uniformly selects an action from turning or moving forward.
    """

    def step(self) -> None:
        action = self.model.random.choice(
            ["turn_left", "turn_right", "turn_backward", "move_forward"]
        )
        if action == "turn_left":
            self.turn_left()
        elif action == "turn_right":
            self.turn_right()
        elif action == "turn_backward":
            self.turn_backward()
        elif action == "move_forward":
            self.move_forward()
