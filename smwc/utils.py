import platform
import subprocess
from typing import List, Optional
from pathlib import Path
import binascii
import sys

from .config import (
    RETROARCH_BIN, 
    RETROARCH_CONFIG_DIR,
    BASE_DIR,
    CLEAN_ROM_DIR
)

def get_bin(path: str, 
            which_cmd_name: str, 
            version_output_substrings: List[str]) -> Optional[Path]:
    
    def run_which() -> Optional[Path]:
      
        try:
            path = subprocess.check_output(
                ['which', which_cmd_name]
            ).decode().strip()
            return Path(path)
        except (subprocess.CalledProcessError,
                PermissionError) as e:
            print(f"{which_cmd_name} is not installed")
            return None
        
    if path:
        bin_path = Path(path)
    else:
        return run_which()
    
    if bin_path.exists():
        try:
            version_output = subprocess.check_output(
                [bin_path, '--version']
            ).decode().strip().lower()
            if any(substr in version_output for substr in version_output_substrings):
                print("Path in config.py is valid")
                return bin_path
            else:
                print(f"This is something other than {which_cmd_name}")
                return None
        except (subprocess.CalledProcessError,
                PermissionError) as e:
            return run_which()
    else:
        return run_which()
    
def locate_retroarch_config_dir(
        specified_config_dir: str = RETROARCH_CONFIG_DIR
    ) -> Path:

    def find_cfg_in_log() -> Path:
        tmp: Path = BASE_DIR / 'tmp.log'
        retroarch_bin = get_bin(
            RETROARCH_BIN, 
            which_cmd_name='retroarch', 
            version_output_substrings=['retroarch']
        )
        cmd: List[str] = [str(retroarch_bin), '--verbose', '--log-file', str(tmp), '&', 'pkill', 'retroarch']
        subprocess.run(cmd)
        with tmp.open('r') as fo:
            lines = fo.readlines()
        config_line_designator = '[INFO] [Config]: Looking for config in: "'
        config_line = [line for line in lines if config_line_designator in line][0]
        config_file = config_line.replace(config_line_designator, '').replace('".\n', '')
        tmp.unlink()
        return Path(config_file).parent

    if specified_config_dir:
        ra_config_dir = Path(specified_config_dir)
        if ra_config_dir.is_dir():
            cfg = ra_config_dir / 'retroarch.cfg'
            if cfg.is_file():
                return ra_config_dir
            return find_cfg_in_log()
        else:
            return find_cfg_in_log()
    else:
        return find_cfg_in_log()


def validate_clean_rom(path: Path) -> bool:
    BASE_CHECKSUM = 0xB19ED489

    try:
        with path.open('rb') as fo:
            buffer = fo.read()
    except FileNotFoundError:
        print(f"\nCannot find a clean Super Mario World rom at\n\t{path}\n")
        print("Try again when you get the right file here.\n")
        sys.exit()

    rom = bytearray(buffer)
    if len(rom) == 0x80200:
        rom = rom[0x200:]

    crc32rom = binascii.crc32(rom)
    if crc32rom != BASE_CHECKSUM:
        print(f'{BASE_CHECKSUM:08X}, got {crc32rom:08X}')
        return False
    return True

def get_clean_rom_path(clean_rom_dir: Path = CLEAN_ROM_DIR) -> Optional[Path]:

    def handle_not_found() -> None:
        try:
            clean_rom_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            pass
        print(f"\nCannot find a clean Vanilla Super Mario World ROM in\n\t{clean_rom_dir}\n")
        print("Try again when you get the right file here.\n")
        sys.exit(1)

    try:
        if clean_rom_dir.is_dir():
            sfcs: List[Path] = list(clean_rom_dir.glob('*.sfc'))
            smcs: List[Path] = list(clean_rom_dir.glob('*.smc'))
            paths = sfcs + smcs
            if paths:
                for path in paths:
                    if validate_clean_rom(path):
                        print("Clean Super Mario World ROM found and validated...")
                        return path
                handle_not_found()
            else:
                handle_not_found()
        else:
            handle_not_found()
    except AttributeError:
        handle_not_found()

    return None
