from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderSettings:
    figure_inches: float
    dpi: int
    drone_size: float
    start_size: float
    grid_linewidth: float
    grid_alpha: float


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def compute_render_settings(width: int, height: int) -> RenderSettings:
    max_dim = max(width, height)

    cell_pixels = _clamp(2000 / max_dim, 14.0, 28.0)
    dpi = 140
    figure_inches = _clamp((max_dim * cell_pixels) / dpi, 8.0, 18.0)

    drone_size = _clamp(10000 / max_dim, 70.0, 220.0)
    start_size = _clamp(drone_size * 2.2, 160.0, 520.0)
    grid_linewidth = _clamp(cell_pixels / 40, 0.25, 0.7)
    grid_alpha = _clamp(cell_pixels / 24, 0.45, 0.9)

    return RenderSettings(
        figure_inches=figure_inches,
        dpi=dpi,
        drone_size=drone_size,
        start_size=start_size,
        grid_linewidth=grid_linewidth,
        grid_alpha=grid_alpha,
    )
