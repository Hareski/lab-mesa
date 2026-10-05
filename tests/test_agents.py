import pytest

from src.agents import Base, Drone
from src.model import Model


class CustomTestDrone(Drone):
    pass


def test_drone_initialization(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    assert drone.front == "N"
    assert drone.cell == model.start_cell
    x, y = drone.cell.coordinate
    assert not model.is_wall((x, y))


def test_drones_are_spawned(small_env_path):
    model = Model(
        env_path=str(small_env_path),
        seed=0,
        n_drones=1,
    )

    for _ in range(5):
        model.step()

    assert len(model.agents_by_type[Base]) == 1
    assert len(model.agents_by_type.get(Drone, [])) == 1


def test_base_spawner_polymorphism(small_env_path):
    model = Model(
        env_path=str(small_env_path),
        seed=0,
        n_drones=1,
        drone_class=CustomTestDrone,
    )

    for _ in range(5):
        model.step()

    assert len(model.agents_by_type.get(CustomTestDrone, [])) == 1


def test_get_possible_moves_excludes_walls(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    moves = drone.get_possible_moves()

    assert moves
    for cell in moves:
        assert not model.is_wall(cell)
        assert not drone.is_wall(cell)


def test_turn_methods(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)
    assert drone.front == "N"

    drone.turn_left()
    assert drone.front == "W"
    drone.turn_left()
    assert drone.front == "S"
    drone.turn_left()
    assert drone.front == "E"
    drone.turn_left()
    assert drone.front == "N"

    drone.turn_right()
    assert drone.front == "E"
    drone.turn_right()
    assert drone.front == "S"
    drone.turn_right()
    assert drone.front == "W"
    drone.turn_right()
    assert drone.front == "N"

    drone.turn_backward()
    assert drone.front == "S"
    drone.turn_backward()
    assert drone.front == "N"


def test_move_forward_and_wall_blocking(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    # In small_env, start is at (2, 3). Cardinal neighbor "S" is (2, 2) which is floor.
    drone.change_direction("S")
    moved = drone.move_forward()
    assert moved
    assert drone.cell.coordinate == (2, 2)

    # Move north back to start (2, 3)
    drone.change_direction("N")
    moved_back = drone.move_forward()
    assert moved_back
    assert drone.cell.coordinate == (2, 3)

    # Moving north again hits wall (2, 4); should fail and keep position
    moved_wall = drone.move_forward()
    assert not moved_wall
    assert drone.cell.coordinate == (2, 3)


def test_north_neighbor_is_wall_robust(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    # In small_env, start is (2, 3) and north neighbor (2, 4) is a wall
    assert drone.north_neighbor_is_wall()


def test_unimplemented_observation_raises(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    with pytest.raises(NotImplementedError):
        drone.observation()


def test_left_neighbor_is_wall(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)
    # In small_env, start is at (2, 3).
    # North neighbor (2, 4) is a wall; South (2, 2), East (3, 3), West (1, 3) are open tunnels.

    drone.front = "E"
    # To left of East is North (2, 4) -> wall
    assert drone.left_neighbor_is_wall() is True

    drone.front = "N"
    # To left of North is West (1, 3) -> tunnel
    assert drone.left_neighbor_is_wall() is False

    drone.front = "S"
    # To left of South is East (3, 3) -> tunnel
    assert drone.left_neighbor_is_wall() is False

    drone.front = "W"
    # To left of West is South (2, 2) -> tunnel
    assert drone.left_neighbor_is_wall() is False


def test_straight_drone_explores(small_env_path):
    from src.algo.straight import StraightDrone
    model = Model(env_path=str(small_env_path), seed=42, drone_class=StraightDrone)
    step = 0
    while model.running and step < 500:
        model.step()
        step += 1
    assert model.is_map_fully_explored()
