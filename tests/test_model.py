from src.model import DEFAULT_MAP_PATH, Model


def test_model_initialization_and_steps():
    model = Model(n_drones=1, seed=0)

    for _ in range(10):
        model.step()

    assert model.width > 0
    assert model.height > 0
    assert len(model.agents_by_type) > 0


def test_default_env_loads_simple():
    assert DEFAULT_MAP_PATH.endswith("simple.csv")

    model = Model()
    assert model.width > 0
    assert model.height > 0

    start_coord = model.start_cell.coordinate
    assert not model.is_wall(start_coord)
    assert model.explored_cells[start_coord[1], start_coord[0]] == 1


def test_custom_env_loads(small_env_path):
    model = Model(env_path=str(small_env_path))

    assert model.width == 16
    assert model.height == 19

    start_coord = model.start_cell.coordinate
    assert not model.is_wall(start_coord)
    assert int((model.env_walls == 0).sum()) == 36


def test_env_file_selects_map():
    model = Model(env_file="complex.csv", seed=0)

    assert model.env_path.endswith("complex.csv")
    assert model.width > 0
    assert model.height > 0


def test_model_terminates_when_fully_explored(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)

    assert not model.is_map_fully_explored()
    assert model.running

    model.explored_cells[model.env_walls == 0] = 1
    assert model.is_map_fully_explored()

    model.step()
    assert not model.running


def test_datacollector_records_steps(small_env_path):
    model = Model(env_path=str(small_env_path), seed=0)
    for _ in range(3):
        model.step()

    df = model.datacollector.get_model_vars_dataframe()
    assert "Explored Cells" in df.columns
    assert "Active Drones" in df.columns
    assert len(df) == 4
