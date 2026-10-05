from __future__ import annotations

import csv
import logging
import os
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
from mesa import Model as MesaModel
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid, PropertyLayer

from src.agents import Base, Drone

if TYPE_CHECKING:
    from mesa.discrete_space import Cell

logger = logging.getLogger("model")

MAPS_DIR = os.path.join(os.path.dirname(__file__), "maps")
DEFAULT_MAP_PATH = os.path.join(MAPS_DIR, "simple.csv")


class Model(MesaModel):
    """
    Simulation model managing global state and the grid.
    """

    def __init__(
        self,
        n_drones: int = 1,
        seed: int | None = None,
        env_path: str | None = None,
        env_file: str | None = None,
        drone_class: type[Drone] | None = None,
        algorithm: str | None = None,
    ) -> None:
        super().__init__(rng=seed)
        self.n_drones = n_drones

        if algorithm is not None and drone_class is None:
            from src.algo import ALGO_MAP
            drone_class = ALGO_MAP.get(algorithm, Drone)

        self.drone_class: type[Drone] = drone_class if drone_class is not None else Drone
        if env_file:
            self.env_path = os.path.join(MAPS_DIR, env_file)
        else:
            self.env_path = env_path or DEFAULT_MAP_PATH

        with open(self.env_path, newline="") as f:
            reader = list(csv.reader(f))

            self.height = len(reader) - 1
            self.width = len(reader[0])

            self.grid = OrthogonalVonNeumannGrid(
                (self.width, self.height), torus=False, random=self.random
            )

            self.env_walls: npt.NDArray[np.float64] = np.zeros(
                [self.height, self.width]
            )

            # Process the CSV rows: reversed so y=0 is at the bottom
            for i, row in enumerate(reversed(reader)):
                if i < self.height:
                    self.env_walls[i] = [float(x) for x in row]
                else:
                    start_x = int(row[0])
                    start_y = self.height - 1 - int(row[1])
                    self.start_cell: Cell = self.grid[(start_x, start_y)]

        self.explored_cells: npt.NDArray[np.float64] = np.zeros(
            [self.height, self.width]
        )
        self.explored_cells[
            self.start_cell.coordinate[1], self.start_cell.coordinate[0]
        ] = 1

        self.grid.add_property_layer(PropertyLayer.from_data("Walls", self.env_walls.T))
        self.grid.add_property_layer(
            PropertyLayer.from_data("Explored Cells", self.explored_cells.T)
        )

        Base(self, cell=self.start_cell)

        self.datacollector = DataCollector(
            model_reporters={
                "Explored Cells": lambda m: int((m.explored_cells == 1).sum()),
                "Explored Ratio": lambda m: float(
                    (m.explored_cells[m.env_walls == 0] == 1).mean()
                ),
                "Active Drones": lambda m: sum(
                    len(agents)
                    for agent_class, agents in m.agents_by_type.items()
                    if issubclass(agent_class, Drone)
                ),
            }
        )
        self.datacollector.collect(self)

    def is_wall(self, cell_or_coord: Cell | tuple[int, ...]) -> bool:
        """
        Returns True if the cell or coordinate is a wall, False otherwise.
        """
        if isinstance(cell_or_coord, tuple):
            coord = cell_or_coord
        else:
            coord = cell_or_coord.coordinate
        return bool(self.grid.Walls.data[coord] == 1)

    def is_map_fully_explored(self) -> bool:
        tunnel_mask = self.env_walls == 0
        explored_tunnels = (tunnel_mask & (self.explored_cells == 1)).sum()
        total_tunnels = tunnel_mask.sum()
        return int(explored_tunnels) == int(total_tunnels)

    def add_to_explored_cells(self) -> None:
        """
        Record all cells visited by active drones.
        """
        for agent_class, agent_set in self.agents_by_type.items():
            if issubclass(agent_class, Drone):
                for agent in agent_set:
                    if isinstance(agent, Drone):
                        x, y = agent.cell.coordinate
                        self.explored_cells[y, x] = 1

    def step(self) -> None:
        """
        Execute one step of the simulation.
        """
        if self.is_map_fully_explored():
            logger.info("Exploration finished!")
            self.running = False
            return

        for agent_class, agent_set in list(self.agents_by_type.items()):
            if issubclass(agent_class, Drone):
                agent_set.do("step")
        if Base in self.agents_by_type:
            self.agents_by_type[Base].do("step")

        # Make new explored cells green in the simulation renderer
        self.add_to_explored_cells()
        self.grid.set_property("Explored Cells", self.explored_cells.T)
        self.datacollector.collect(self)
