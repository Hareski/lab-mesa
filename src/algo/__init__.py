from __future__ import annotations

from src.algo.flooding import FloodingDrone
from src.algo.lefthand import LeftHandDrone
from src.algo.light_test import LightTestDrone
from src.algo.random import RandomDrone
from src.algo.return_base import ReturnDrone
from src.algo.straight import StraightDrone

ALGO_MAP = {
    "Random Walk": RandomDrone,
    "Straight Corridor": StraightDrone,
    "Left-Hand Rule": LeftHandDrone,
    "Flooding Exploration": FloodingDrone,
    "Light Test": LightTestDrone,
    "Return to Base": ReturnDrone,
}

__all__ = [
    "ALGO_MAP",
    "FloodingDrone",
    "LeftHandDrone",
    "LightTestDrone",
    "RandomDrone",
    "ReturnDrone",
    "StraightDrone",
]
