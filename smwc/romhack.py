from pathlib import Path
from typing import Optional, List, Tuple
import subprocess 
import sys

from smwc import db
from .config import (
    RETROARCH_CONFIG_DIR,
    RETROARCH_BIN,
    SNES_CORE,
    DEFAULT_RA_CONFIG,
    MODIFIED_RA_CONFIG
)
from .utils import get_bin

class SMWRomhack:
    def __init__(self, sfc_file: str):
        self.sfc: Path = Path(sfc_file)
        self.srm : Optional[Path] = self.get_srm_from_sfc(sfc_file)

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

        def modify_cfg(old: str, new: str, subprocess_cmd: List[str]) -> None:
            init_new_cfg((old, new))
            for additional_arg in ['-c', MODIFIED_RA_CONFIG]:
                subprocess_cmd.append(additional_arg)
            return subprocess_cmd
        
        def init_new_cfg(mod: List[Tuple]):
            if MODIFIED_RA_CONFIG.exists():
                MODIFIED_RA_CONFIG.unlink()

            with DEFAULT_RA_CONFIG.open() as rfo:
                cfg_text = rfo.read()

            modified_cfg_text = cfg_text.replace(mod[0], mod[1])

            with MODIFIED_RA_CONFIG.open('w') as wfo:
                wfo.write(modified_cfg_text)

        retroarch_bin = get_bin(
            RETROARCH_BIN, 
            which_cmd_name='retroarch', 
            version_output_substrings=['retroarch']
        )
        cmd: List = [retroarch_bin, '-L', SNES_CORE, self.sfc]

        if rewind:
            cmd = modify_cfg('rewind_enable = "false"',
                             'rewind_enable = "true"', cmd)
            
        if not rewind and rewind is not None:
            cmd = modify_cfg('rewind_enable = "true"',
                             'rewind_enable = "false"', cmd)

        subprocess.run(cmd)

        self.post_launch()

    def post_launch(self):
        self.srm = self.get_srm_from_sfc(self.sfc)
        self.update_exit_clear_count()

    def update_exit_clear_count(self):
        count_from_srm: int = self.get_exit_clear_count()
        try:
            hack = db.select_hack_by('path', str(self.sfc))[0]
        except IndexError as e:
            print(e)

        if count_from_srm != hack['exits_cleared']:
            update_sql: str = db.read('smwc/sql/update_exits_cleared.sql')

            db.execute(update_sql, (count_from_srm, hack['id']))
            print(f"{hack['title']} updated exits_cleared from {hack['exits_cleared']} to {count_from_srm}")