from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents import Base
from src.algo.flooding import FloodingDrone

if TYPE_CHECKING:
    from mesa.discrete_space import Cell


class ReturnDrone(FloodingDrone):
    """
    Explore with the flooding policy, then follow a light signal and return.

    The route to base is recomputed from the map at each step; no visited-cell
    or movement-history state is kept.
    """

    def __init__(self, model, cell: Cell) -> None:
        super().__init__(model, cell)
        self.moves_to_base: list[str] = []

    def is_agent_light_off(self, cell: Cell) -> bool:
        """Return whether a drone in this cell has its light off."""
        return any(
            isinstance(agent, ReturnDrone) and not (agent.light_red or getattr(agent, "light", False))
            for agent in cell.agents
        )

    def is_agent_light_on(self, cell: Cell) -> bool:
        """Return whether a drone in this cell has its light on."""
        return any(
            isinstance(agent, ReturnDrone) and (agent.light_red or getattr(agent, "light", False))
            for agent in cell.agents
        )

    def is_agent_light_red(self, cell: Cell) -> bool:
        """Return whether a drone in this cell has its light_red on."""
        return self.is_agent_light_on(cell)

    def is_agent_light_blue(self, cell: Cell) -> bool:
        """Return whether a drone in this cell has its light_blue on."""
        return any(
            isinstance(agent, ReturnDrone) and (agent.light_blue or getattr(agent, "inter", False))
            for agent in cell.agents
        )

    def is_agent_inter(self, cell: Cell) -> bool:
        """Alias for backwards compatibility."""
        return self.is_agent_light_blue(cell)

    def _cell_wall(self, cell: Cell | None, allow_base: bool = False) -> bool:
        """A cell is blocked for movement/trigger if it is a wall, off-grid,
        or occupied. occupant is ignored when allow_base and the only
        occupants are the Base station."""
        return cell is None or self.model.is_wall(cell)


    def _cell_blocked(self, cell: Cell | None, allow_base: bool = False) -> bool:
        """A cell is blocked for movement/trigger if it is a wall, off-grid,
        or occupied. occupant is ignored when allow_base and the only
        occupants are the Base station."""
        if cell is None:
            return True
        if self.model.is_wall(cell):
            return True
        agents = cell.agents
        if not agents:
            return False
        return not (allow_base and all(isinstance(a, Base) for a in agents))

    def _agent_orientation(self, cell: Cell) -> str | None:
        """Return the orientation of the agent in front."""
        if cell is None:
            assert False, "Cell is None"
            return None
        assert len(cell.agents) > 0, "Cell has no agents"
        for agent in cell.agents:
            if isinstance(agent, ReturnDrone):
                return agent.front
        return None

    def _neighbors(self) -> tuple[Cell | None, Cell | None, Cell | None, Cell | None]:
        left = self.get_cardinal_neighbor(self.relative_to_cardinal("LEFT"))
        front = self.get_cardinal_neighbor(self.relative_to_cardinal("FRONT"))
        right = self.get_cardinal_neighbor(self.relative_to_cardinal("RIGHT"))
        back = self.get_cardinal_neighbor(self.relative_to_cardinal("BACK"))
        return left, front, right, back

    def around_base(self) -> bool:
        for neighbor in self.cell.neighborhood:
            if any(isinstance(agent, Base) for agent in neighbor.agents):
                return True
        return any(isinstance(agent, Base) for agent in self.cell.agents)

    def step(self) -> None:
        back_dir = self.relative_to_cardinal("BACKWARD")
        backward_cell = self.get_cardinal_neighbor(back_dir)

        left = self.get_cardinal_neighbor(self.relative_to_cardinal("LEFT"))
        front = self.get_cardinal_neighbor(self.relative_to_cardinal("FRONT"))
        right = self.get_cardinal_neighbor(self.relative_to_cardinal("RIGHT"))
        open_moves_forward = self.get_open_moves([mv for mv in (left, front, right)
            if mv is not None])


        if self.light_blue:
            if self.moves_to_base:
                last_move = self.moves_to_base.pop()
                if front in open_moves_forward:
                    if last_move == "LEFT":
                        self.move_forward()
                        self.turn_right()
                    elif last_move == "RIGHT":
                        self.move_forward()
                        self.turn_left()
                    else:
                        self.move_forward()
                else:
                    self.moves_to_base.append(last_move)
                    return
            return

        if not self.light_red:
            if open_moves_forward and (self.around_base() or (backward_cell is not None
                and self.is_cell_blocked(backward_cell))):
                self.light_red = False
                next_move = self.random.choice(open_moves_forward)
                if next_move == left:
                    self.turn_left()
                    self.move_forward()
                    self.moves_to_base.append("LEFT")
                elif next_move == right:
                    self.turn_right()
                    self.move_forward()
                    self.moves_to_base.append("RIGHT")
                else:
                    self.move_forward()
                    self.moves_to_base.append("FRONT")
                return
            if backward_cell and self.is_agent_light_on(backward_cell):
                self.light_red = True
                return
            if self.around_base():
                self.light_red = True
                return

        if self.light_red:
            if all(self._cell_wall(c) for c in (left, front, right)):
                self.light_red = False
                self.light_blue = True
                self.turn_backward()
                return
            if (any(self.is_agent_light_blue(c) for c in (left, right, front,
                backward_cell) if c is not None) and not open_moves_forward):
                self.light_red = True
                self.light_blue = True
                self.turn_backward()
                return
            if open_moves_forward:
                self.light_red = False
                next_move = self.random.choice(open_moves_forward)
                if next_move == left:
                    self.turn_left()
                    self.move_forward()
                    self.moves_to_base.append("LEFT")
                elif next_move == right:
                    self.turn_right()
                    self.move_forward()
                    self.moves_to_base.append("RIGHT")
                else:
                    self.move_forward()
                    self.moves_to_base.append("FRONT")
                return
