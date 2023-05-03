from pathlib import Path
from typing import Optional

from .config import RETROARCH_CONFIG_DIR

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
    
    @staticmethod
    def read_memory_address(hex: int, path: Path) -> int:
        with path.open('rb') as fo:
            fo.seek(hex)
            data = fo.read(1)
            return int.from_bytes(data, byteorder="little")
        

    def get_exit_clear_count(self) -> Optional[int]:
        MEMORY_ADDRESS: int = 0x8C
        if self.srm is not None:
            try:
                return self.read_memory_address(
                    MEMORY_ADDRESS, self.srm
                )
            except FileNotFoundError:
                print(f"SRAM Does Not Exist: {self.srm}")
