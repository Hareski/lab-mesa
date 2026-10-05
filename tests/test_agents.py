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

    # In small_env, start is at (1, 9). Cardinal neighbor "E" is (2, 9) which is floor.
    drone.change_direction("E")
    moved = drone.move_forward()
    assert moved
    assert drone.cell.coordinate == (2, 9)

    # Move west back to start (1, 9)
    drone.change_direction("W")
    moved_back = drone.move_forward()
    assert moved_back
    assert drone.cell.coordinate == (1, 9)

    # Moving south from start hits a wall (1, 8); should fail and keep position
    drone.change_direction("S")
    moved_wall = drone.move_forward()
    assert not moved_wall
    assert drone.cell.coordinate == (1, 9)


def test_north_neighbor_is_wall_robust(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    # In small_env, start is (1, 9) and north neighbor (1, 10) is a wall
    assert drone.north_neighbor_is_wall()


def test_unimplemented_observation_raises(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)

    with pytest.raises(NotImplementedError):
        drone.observation()


def test_left_neighbor_is_wall(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone = Drone(model, cell=model.start_cell)
    # In small_env, start is at (1, 9).
    # North (1, 10), South (1, 8), West (0, 9) are walls; East (2, 9) is an open tunnel.

    drone.front = "E"
    # To left of East is North (1, 10) -> wall
    assert drone.left_neighbor_is_wall() is True

    drone.front = "N"
    # To left of North is West (0, 9) -> wall
    assert drone.left_neighbor_is_wall() is True

    drone.front = "S"
    # To left of South is East (2, 9) -> tunnel
    assert drone.left_neighbor_is_wall() is False

    drone.front = "W"
    # To left of West is South (1, 8) -> wall
    assert drone.left_neighbor_is_wall() is True


def test_straight_drone_explores(small_env_path):
    from src.algo.straight import StraightDrone
    model = Model(env_path=str(small_env_path), seed=42, drone_class=StraightDrone)
    step = 0
    while model.running and step < 500:
        model.step()
        step += 1
    assert model.is_map_fully_explored()


def test_lefthand_drone_explores_simple_and_t_shape():
    from src.algo.lefthand import LeftHandDrone
    # Test simple map
    m_simple = Model(env_file="simple.csv", drone_class=LeftHandDrone, seed=0)
    for _ in range(100):
        if not m_simple.running:
            break
        m_simple.step()
    assert m_simple.is_map_fully_explored()

    # Test T-shape map
    m_t = Model(env_file="t_shape.csv", drone_class=LeftHandDrone, seed=0)
    for _ in range(30):
        if not m_t.running:
            break
        m_t.step()
    assert m_t.is_map_fully_explored()


def test_flooding_drone_explores(small_env_path):
    from src.algo.flooding import FloodingDrone
    model = Model(env_path=str(small_env_path), seed=42, drone_class=FloodingDrone, n_drones=100)
    step = 0
    while model.running and step < 200:
        model.step()
        step += 1
    assert model.is_map_fully_explored()


def test_drone_light_attribute(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    drone1 = Drone(model, cell=model.start_cell)
    assert drone1.light is False
    drone1.toggle_light()
    assert drone1.light is True

    # Neighboring open cell (2, 9), east of the start
    drone2 = Drone(model, cell=model.grid[(2, 9)])
    assert drone2.neighbors_have_light_on() is True
    drone1.toggle_light()
    assert drone2.neighbors_have_light_on() is False


def test_return_drone(small_env_path):
    from src.algo.return_base import ReturnDrone
    model = Model(env_path=str(small_env_path), seed=42, drone_class=ReturnDrone, n_drones=3, require_return=True)
    steps = 0
    while model.running and steps < 200:
        model.step()
        steps += 1
    assert model.is_map_fully_explored()
    assert len(model.active_drones()) == 0
