from __future__ import annotations

from src.algo.flooding import FloodingDrone


class LightTestDrone(FloodingDrone):
    """
    Exercise 5 (Question 17):
    - 1% of the time at random, toggles light.
    - if light is Off and a neighbor has light On, turns light On.
    - otherwise follows flooding policy.
    """

    def step(self) -> None:
        if self.model.random.random() < 0.01:
            self.toggle_light()
            return

        if not self.light_red and self.neighbors_have_light_on():
            self.light_red = True
            return

        super().step()
