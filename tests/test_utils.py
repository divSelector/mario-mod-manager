import pytest
from pathlib import Path
import platform

from smwc.utils import (
    get_bin, 
    locate_retroarch_config_dir, 
    validate_clean_rom, 
    get_clean_rom_path
)
from smwc.config import BASE_DIR


class TestGetBin:

    @pytest.mark.skipif(platform.system() == 'Windows', reason='This test is for POSIX systems only')
    def test_found_from_blank_path_in_config(self) -> None:
        bin_path = get_bin('', 'bash', ['gnu bash'])
        if bin_path is not None:
            assert bin_path.exists()

    @pytest.mark.skipif(platform.system() == 'Windows', reason='This test is for POSIX systems only')
    def test_found_from_nonexisting_path_in_config(self) -> None:
        bin_path = get_bin('/does/not/exist', 'bash', ['gnu bash'])
        if bin_path is not None:
            assert bin_path.exists()

    @pytest.mark.skipif(platform.system() == 'Windows', reason='This test is for POSIX systems only')
    def test_found_from_existing_path_in_config(self) -> None:
        bin_path = get_bin('/bin/bash', 'bash', ['gnu bash'])
        if bin_path is not None:
            assert bin_path.exists() and str(bin_path) == '/bin/bash'


class TestLocateRetroarchConfigDir:

    def test_found_from_nonexisting_path_in_config(self) -> None:
        config_dir = locate_retroarch_config_dir('/does/not/exist')
        assert config_dir.is_dir() and str(config_dir) != '/does/not/exist' 

    def test_found_from_no_path_specified_in_config(self) -> None:
        config_dir = locate_retroarch_config_dir('')
        assert config_dir.is_dir() and config_dir != BASE_DIR

    def test_found_from_existing_path_in_config(self, mock_ra_config_dir: str) -> None:
        # Mock the find_cfg_in_log function to raise an exception if called
        config_dir = locate_retroarch_config_dir(mock_ra_config_dir)
            
        # Assert that the returned path is equal to the supplied path
        assert config_dir == mock_ra_config_dir


class TestValidateCleanRom:

    def test_is_valid(self) -> None:
        rom_path = Path('roms/clean/cleansmw.sfc')
        assert validate_clean_rom(rom_path)
        
    def test_is_invalid(self) -> None:
        rom_path = Path('roms/clean/unclean.sfc')
        assert not validate_clean_rom(rom_path)

    def test_not_found(self) -> None:
        rom_path = Path('roms/clean/doesnotexist.sfc')
        with pytest.raises(SystemExit):
            validate_clean_rom(rom_path)


class TestGetCleanRomPath:

    def test_valid_sfc_in_dir(self) -> None:
        clean_rom_path = get_clean_rom_path(Path('roms/clean'))
        if clean_rom_path is not None:
            assert clean_rom_path.is_file()

    def test_only_invalid_sfc_in_dir(self, mock_not_clean_rom_dir: Path) -> None:
        with pytest.raises(SystemExit):
            get_clean_rom_path(mock_not_clean_rom_dir)

    def test_empty_dir(self, mock_empty_dir: Path) -> None:
        with pytest.raises(SystemExit):
            get_clean_rom_path(mock_empty_dir)

    def test_dir_does_not_exist(self) -> None:
        with pytest.raises(SystemExit):
            get_clean_rom_path(Path("/self/love/"))