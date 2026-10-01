from src.rendering import compute_render_settings


def test_settings_for_small_grid():
    settings = compute_render_settings(16, 19)

    assert settings.dpi == 140
    assert settings.drone_size > 0
    assert settings.start_size > settings.drone_size


def test_settings_clamp_large_grids():
    settings = compute_render_settings(1000, 1000)

    assert settings.figure_inches == 18.0
    assert settings.drone_size == 70.0
    assert settings.start_size == 160.0


def test_settings_scale_with_size():
    small = compute_render_settings(20, 20)
    large = compute_render_settings(200, 200)

    assert large.figure_inches >= small.figure_inches
    assert large.grid_linewidth <= small.grid_linewidth
    assert large.drone_size <= small.drone_size
