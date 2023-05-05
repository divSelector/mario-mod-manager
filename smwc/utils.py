import platform
import subprocess
from typing import List
from pathlib import Path
import time

from .config import (
    RETROARCH_BIN, 
    FLIPS_BIN, 
    RETROARCH_CONFIG_DIR,
    SNES_CORE,
    CLEAN_ROM, 
    BASE_DIR
)

def check_output(cmd: List[str]):
    if platform.system() != 'Windows':
        return subprocess.check_output(cmd).decode().strip()
        

def get_bin(path: str, which_cmd_name: str, version_output_substrings: List[str]):
    
    def run_which():
        if platform.system() != 'Windows':
            try:
                path = check_output(['which', which_cmd_name])
                # print(f"`which {which_cmd_name}` found a binary...")
                return path
            except (subprocess.CalledProcessError,
                    PermissionError) as e:
                print(f"{which_cmd_name} is not installed")
                return ''

    if path:
        bin_path = Path(path)
    else:
        return run_which()
    
    if bin_path.exists():
        try:
            # any(substring in string for substring in substrings)
            version_output = check_output([bin_path, '--version']).lower()
            if any(substr in version_output for substr in version_output_substrings):
                print("Path in config.py is valid")
                return bin_path
            else:
                print(f"This is something other than {which_cmd_name}")
        except (subprocess.CalledProcessError,
                PermissionError) as e:
            return run_which()
    else:
        return run_which()
    
def locate_retroarch_config_dir() -> Path:

    def find_cfg_in_log():
        tmp: Path = BASE_DIR / 'tmp.log'
        retroarch_bin = get_bin(
            RETROARCH_BIN, 
            which_cmd_name='retroarch', 
            version_output_substrings=['retroarch']
        )
        cmd: List[str] = [retroarch_bin, '--verbose', '--log-file', tmp, '&', 'pkill', 'retroarch']
        subprocess.run(cmd)
        with tmp.open('r') as fo:
            lines = fo.readlines()
        config_line_designator = '[INFO] [Config]: Looking for config in: "'
        config_line = [line for line in lines if config_line_designator in line][0]
        config_file = config_line.replace(config_line_designator, '').replace('".\n', '')
        tmp.unlink()
        return Path(config_file).parent


    if RETROARCH_CONFIG_DIR:
        ra_config_dir = Path(RETROARCH_CONFIG_DIR)
        if ra_config_dir.is_dir():
            cfg = ra_config_dir / 'retroarch.cfg'
            if cfg.is_file():
                return ra_config_dir
        else:
            return find_cfg_in_log()
    else:
        return find_cfg_in_log()


