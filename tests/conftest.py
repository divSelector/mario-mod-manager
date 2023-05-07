import pytest

@pytest.fixture
def mock_config_dir(tmp_path):
    # Create a temporary directory and add a retroarch.cfg file to it
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    cfg = config_dir / "retroarch.cfg"
    cfg.touch()
    return config_dir