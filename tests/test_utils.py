import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from smwc.utils import (
    get_bin, 
    locate_retroarch_config_dir, 
    validate_clean_rom, 
    get_clean_rom_path
)

class TestGetBin:

    def test_found_from_nonexisting_path_in_config(self):
        bin_path = get_bin('', 'bash', ['GNU bash'])
        assert bin_path.exists()

    def test_found_from_existing_path_in_config(self):
        bin_path = get_bin('/bin/bash', 'bash', ['bash'])
        assert bin_path.exists() and str(bin_path) == '/bin/bash'


class TestLocateRetroarchConfigDir:

    def test_found_from_nonexisting_path_in_config(self):
        config_dir = locate_retroarch_config_dir('/does/not/exist')
        assert config_dir.is_dir() and str(config_dir) != '/does/not/exist' 

    def test_found_from_existing_path_in_config(self, mock_config_dir):
        # Mock the find_cfg_in_log function to raise an exception if called
        config_dir = locate_retroarch_config_dir(mock_config_dir)
            
        # Assert that the returned path is equal to the supplied path
        assert config_dir == mock_config_dir

class TestValidateCleanRom:

    def test_is_valid(self):
        rom_path = Path('roms/clean/cleansmw.sfc')
        assert validate_clean_rom(rom_path)
        
    def test_is_invalid(self):
        rom_path = Path('roms/clean/unclean.sfc')
        assert not validate_clean_rom(rom_path)

    def test_not_found(self):
        rom_path = Path('roms/clean/doesnotexist.sfc')
        with pytest.raises(SystemExit):
            validate_clean_rom(rom_path)


def test_get_clean_rom_path():
    clean_rom_path = get_clean_rom_path()
    assert clean_rom_path.is_file()
