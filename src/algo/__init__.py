from __future__ import annotations

from src.algo.random import RandomDrone
from src.algo.straight import StraightDrone

ALGO_MAP = {
    "Random Walk": RandomDrone,
    "Straight Corridor": StraightDrone,
}

__all__ = ["ALGO_MAP", "RandomDrone", "StraightDrone"]
