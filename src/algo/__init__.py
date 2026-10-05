from __future__ import annotations

from src.algo.flooding import FloodingDrone
from src.algo.lefthand import LeftHandDrone
from src.algo.random import RandomDrone
from src.algo.straight import StraightDrone

ALGO_MAP = {
    "Random Walk": RandomDrone,
    "Straight Corridor": StraightDrone,
    "Left-Hand Rule": LeftHandDrone,
    "Flooding Exploration": FloodingDrone,
}

__all__ = [
    "ALGO_MAP",
    "FloodingDrone",
    "LeftHandDrone",
    "RandomDrone",
    "StraightDrone",
]
