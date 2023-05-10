import pytest
from pathlib import Path
from typing import List, Dict
from smwc.scraper import SMWCentralScraper

# utils.py
@pytest.fixture
def mock_ra_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    cfg = config_dir / "retroarch.cfg"
    cfg.touch()
    return config_dir

@pytest.fixture
def mock_not_clean_rom_dir(tmp_path: Path) -> Path:
    clean_rom_dir = tmp_path / "clean"
    clean_rom_dir.mkdir()
    sfc = clean_rom_dir / 'clean.sfc'
    sfc.touch()
    return clean_rom_dir

@pytest.fixture
def mock_empty_dir(tmp_path: Path) -> Path:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    return empty_dir


# scraper.py
@pytest.fixture(scope="session")
def mock_scraper() -> SMWCentralScraper:
    return SMWCentralScraper(
        'https://raw.githubusercontent.com/divSelector/smwcentral-scraper/main/tests/mocks/smwcentral-hack-list-html.txt'
    )

@pytest.fixture(scope="session")
def mock_scraped_page(mock_scraper: SMWCentralScraper) -> str:
    return  mock_scraper.get_page_content(
        mock_scraper.hacks_url
    )