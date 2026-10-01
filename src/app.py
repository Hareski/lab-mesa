# ruff: noqa: E402
# pyright: reportAttributeAccessIssue=none, reportCallIssue=none
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

_repo_root = str(Path(__file__).resolve().parents[1])
if sys.path[0] != _repo_root:
    sys.path.insert(0, _repo_root)

from matplotlib.figure import Figure
from mesa.visualization import SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

from src.agents import Base, Drone
from src.model import MAPS_DIR, Model
from src.rendering import compute_render_settings

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from mesa.agent import Agent
    from mesa.discrete_space import PropertyLayer

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

model = Model()
render_settings = compute_render_settings(model.width, model.height)

MAP_FILES = sorted(p.name for p in Path(MAPS_DIR).glob("*.csv"))


def propertylayer_portrayal(layer: PropertyLayer) -> PropertyLayerStyle | None:
    if layer.name == "Walls":
        return PropertyLayerStyle(
            color="black", colorbar=False, alpha=1, vmin=0, vmax=1
        )
    if layer.name == "Explored Cells":
        return PropertyLayerStyle(
            color="green", colorbar=False, alpha=0.5, vmin=0, vmax=1
        )
    return None


def agent_color(agent: Agent) -> str:
    if isinstance(agent, Base):
        return "blue"
    if isinstance(agent, Drone):
        return "red"
    return "gray"


def agent_shape(agent: Agent) -> str:
    if isinstance(agent, Base):
        return "s"
    if isinstance(agent, Drone):
        if agent.front == "E":
            return ">"
        if agent.front == "N":
            return "^"
        if agent.front == "W":
            return "<"
        if agent.front == "S":
            return "v"
    return "o"


def agent_portrayal(agent: Agent) -> AgentPortrayalStyle:
    model_instance = cast(Model, agent.model)
    settings = compute_render_settings(model_instance.width, model_instance.height)
    color = agent_color(agent)
    marker = agent_shape(agent)
    if isinstance(agent, Base):
        return AgentPortrayalStyle(
            color=color,
            marker=marker,
            size=settings.start_size,
            zorder=0,
            alpha=0.5,
            edgecolors="black",
            linewidths=1.0,
        )
    if isinstance(agent, Drone):
        return AgentPortrayalStyle(
            color=color,
            marker=marker,
            size=settings.drone_size,
            zorder=1,
            alpha=1.0,
            edgecolors="black",
            linewidths=1.0,
        )
    return AgentPortrayalStyle(color=color, marker=marker)


def post_process_space(ax: Axes) -> None:
    width = int(round(ax.get_xlim()[1] - ax.get_xlim()[0]))
    height = int(round(ax.get_ylim()[1] - ax.get_ylim()[0]))
    settings = compute_render_settings(width, height)

    figure = cast(Figure, ax.figure)
    figure.set_dpi(settings.dpi)
    figure.set_size_inches(settings.figure_inches, settings.figure_inches)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    for line in ax.lines:
        line.set_linewidth(settings.grid_linewidth)
        line.set_alpha(settings.grid_alpha)


renderer: Any = SpaceRenderer(model, backend="matplotlib")
if hasattr(renderer, "setup_structure"):
    renderer.setup_structure(
        figsize=(render_settings.figure_inches, render_settings.figure_inches),
        dpi=render_settings.dpi,
    )
renderer.draw_structure()

if hasattr(renderer, "setup_propertylayer"):
    renderer.setup_propertylayer(propertylayer_portrayal)
    renderer.draw_propertylayer()
else:
    renderer.draw_propertylayer(propertylayer_portrayal)

if hasattr(renderer, "setup_agents"):
    renderer.setup_agents(agent_portrayal)
    renderer.draw_agents()
else:
    renderer.draw_agents(agent_portrayal)

renderer.post_process = post_process_space

model_params = {
    "env_file": {
        "type": "Select",
        "value": "simple.csv",
        "values": MAP_FILES,
        "label": "Environment",
    },
    "n_drones": {
        "type": "SliderInt",
        "value": 1,
        "label": "Number of Drones",
        "min": 1,
        "max": 500,
        "step": 1,
    },
}

page = SolaraViz(
    model,
    renderer,
    model_params=model_params,
    name="Mesa",
    play_interval=100,
    render_interval=1,
    width="100%",
    height="90vh",
)
