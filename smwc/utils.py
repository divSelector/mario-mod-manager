import platform
import subprocess
from typing import List
from pathlib import Path

from .config import (
    RETROARCH_BIN, 
    FLIPS_BIN, 
    RETROARCH_CONFIG_DIR,
    SNES_CORE,
    CLEAN_ROM
)

def check_output(cmd: List[str]):
    if platform.system() != 'Windows':
        return subprocess.check_output(cmd).decode().strip()
        

def get_bin(path: str, which_cmd_name: str, version_output_substrings: List[str]):
    
    def run_which():
        if platform.system() != 'Windows':
            try:
                path = check_output(['which', which_cmd_name])
                print(f"`which {which_cmd_name}` found a binary...")
                return path
            except subprocess.CalledProcessError as e:
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