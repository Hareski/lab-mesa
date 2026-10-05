import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# First row is the start cell (x, y, then empty cells to match the map width),
# the following rows are the map from top to bottom: 0 = tunnel, 1 = wall.
SMALL_ENV_CSV = """\
1,9,,,,,,,,,,,,,,
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1
1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
"""


@pytest.fixture
def small_env_path(tmp_path):
    env_path = tmp_path / "small_env.csv"
    env_path.write_text(SMALL_ENV_CSV, encoding="utf-8")
    return env_path
