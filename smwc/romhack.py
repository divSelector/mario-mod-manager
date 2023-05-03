from pathlib import Path
from typing import Optional, List, Tuple
import subprocess 

from .config import (
    RETROARCH_CONFIG_DIR,
    RETROARCH_BIN,
    SNES_CORE,
    DEFAULT_RA_CONFIG,
    MODIFIED_RA_CONFIG
)

class SMWRomhack:
    def __init__(self, sfc_file: str):
        self.sfc: Path = Path(sfc_file)
        self.srm : Path = self.get_srm_from_sfc(sfc_file)

    @staticmethod
    def get_srm_from_sfc(sfc_file: str) -> Optional[Path]:
        sfc_path = Path(sfc_file)
        srm_filename = sfc_path.stem + ".srm"
        srm_path = RETROARCH_CONFIG_DIR / 'saves' / srm_filename
        return srm_path if srm_path.exists() else None
    
    def read_memory_address(self, hex: int, size_bytes: int = 1) -> int:
        if self.srm is not None and self.srm.exists():
            with self.srm.open('rb') as fo:
                fo.seek(hex)
                data = fo.read(size_bytes)
                return int.from_bytes(data, byteorder="little")
        else:
            print(f"SRAM Does Not Exist: {self.srm}")

        
    def get_exit_clear_count(self) -> int:
        MEMORY_ADDRESS: int = 0x8C
        SA1_MEMORY_ADDRESS: int = 0x1C08C
        value = self.read_memory_address(MEMORY_ADDRESS)
        sa1_value = self.read_memory_address(SA1_MEMORY_ADDRESS)
        return sa1_value if sa1_value != 0 else value
    
    def launch_in_retroarch(self, rewind: bool) -> None:

        def modify(old: str, new: str, subprocess_cmd: List[str]) -> None:
            _modify_retroarch_config((old, new))
            for additional_arg in ['-c', MODIFIED_RA_CONFIG]:
                subprocess_cmd.append(additional_arg)
            return subprocess_cmd
        
        def _modify_retroarch_config(mod: List[Tuple]):
            if MODIFIED_RA_CONFIG.exists():
                MODIFIED_RA_CONFIG.unlink()

            with DEFAULT_RA_CONFIG.open() as rfo:
                cfg_text = rfo.read()

            modified_cfg_text = cfg_text.replace(mod[0], mod[1])

            with MODIFIED_RA_CONFIG.open('w') as wfo:
                wfo.write(modified_cfg_text)

        cmd: List = [RETROARCH_BIN, '-L', SNES_CORE, self.sfc]

        if rewind:
            cmd = modify('rewind_enable = "false"',
                        'rewind_enable = "true"', cmd)
            
        if not rewind and rewind is not None:
            cmd = modify('rewind_enable = "true"',
                        'rewind_enable = "false"', cmd)

        subprocess.run(cmd)
