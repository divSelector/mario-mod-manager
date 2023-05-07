from pathlib import Path
from typing import Optional, List, Tuple, Any, Union
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
from .utils import get_bin, locate_retroarch_config_dir
from .downloader import ROMHACKS_DIR

class SMWRomhack:
    def __init__(self, sfc_file: str):
        self.sfc: Path = ROMHACKS_DIR / sfc_file
        self.ra_config_dir: Path = locate_retroarch_config_dir()
        print(self.ra_config_dir)
        self.srm : Optional[Path] = self.get_srm_from_sfc(sfc_file)
        


    def get_srm_from_sfc(self, sfc_file: Union[str, Path]) -> Optional[Path]:
        sfc_path = Path(sfc_file)
        srm_filename = sfc_path.stem + ".srm"
        srm_path = self.ra_config_dir / 'saves' / srm_filename
        return srm_path if srm_path.exists() else None
    

    def read_memory_address(self, hex: int, size_bytes: int = 1) -> int:
        if self.srm is not None and self.srm.exists():
            with self.srm.open('rb') as fo:
                fo.seek(hex)
                data = fo.read(size_bytes)
                return int.from_bytes(data, byteorder="little")
        else:
            print(f"SRAM Does Not Exist: {self.srm}")
            return 0

        
    def get_exit_clear_count(self) -> int:
        MEMORY_ADDRESS: int = 0x8C
        SA1_MEMORY_ADDRESS: int = 0x1C08C
        value = self.read_memory_address(MEMORY_ADDRESS)
        sa1_value = self.read_memory_address(SA1_MEMORY_ADDRESS)
        return sa1_value if sa1_value != 0 else value
    
    def launch_in_retroarch(self, rewind: bool) -> None:

        def modify_cfg(old: str, new: str, subprocess_cmd: List[str]) -> List[str]:
            modified_ra_cfg: Path = self.ra_config_dir / MODIFIED_RA_CONFIG
            init_new_cfg((old, new))
            for additional_arg in ['-c', str(modified_ra_cfg)]:
                subprocess_cmd.append(additional_arg)
            return subprocess_cmd
        
        def init_new_cfg(mod: Tuple[Any, Any]) -> None:
            default_ra_cfg: Path = self.ra_config_dir / DEFAULT_RA_CONFIG
            modified_ra_cfg: Path = self.ra_config_dir / MODIFIED_RA_CONFIG
            if modified_ra_cfg.exists():
                modified_ra_cfg.unlink()

            with default_ra_cfg.open() as rfo:
                cfg_text = rfo.read()


            modified_cfg_text = cfg_text.replace(str(mod[0]), str(mod[1]))

            with modified_ra_cfg.open('w') as wfo:
                wfo.write(modified_cfg_text)

        retroarch_bin = get_bin(
            RETROARCH_BIN, 
            which_cmd_name='retroarch', 
            version_output_substrings=['retroarch']
        )
        snes_core: Path = self.ra_config_dir / SNES_CORE
        cmd: List = [retroarch_bin, '-L', snes_core, self.sfc]

        if rewind:
            cmd = modify_cfg('rewind_enable = "false"',
                             'rewind_enable = "true"', cmd)
            
        if not rewind and rewind is not None:
            cmd = modify_cfg('rewind_enable = "true"',
                             'rewind_enable = "false"', cmd)

        subprocess.run(cmd)

        self.post_launch()

    def post_launch(self) -> None:
        self.srm = self.get_srm_from_sfc(self.sfc)
        self.update_exit_clear_count()

    def update_exit_clear_count(self) -> None:
        count_from_srm: int = self.get_exit_clear_count()
        try:
            print(self.sfc)
            hack = db.select_hack_by('path', self.sfc.name)[0]
        except IndexError as e:
            print(e)


        update_sql: str = db.read('smwc/sql/update_exits_cleared.sql')

        db.execute(update_sql, (count_from_srm, hack['id']))
        print(f"{hack['title']} updated exits_cleared from {hack['exits_cleared']} to {count_from_srm}")