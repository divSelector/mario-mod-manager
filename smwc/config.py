from pathlib import Path

DEBUG_SCRAPER = {
    "ONE_PAGE_ONLY": False,
    "ONE_HACK_ONLY": False
}

TMP_PATH = Path('tmp')
ZIPS_DL_PATH = TMP_PATH / 'zips'
ZIP_DL_PATH = TMP_PATH / 'tmp'
BPS_PATH = TMP_PATH / 'bps'

RETROARCH_BIN = '/usr/local/bin/retroarch'
RETROARCH_CONFIG_DIR = Path.home() / '.config/retroarch'
SNES_CORE = RETROARCH_CONFIG_DIR / 'cores/snes9x_libretro.so'
DEFAULT_RA_CONFIG = RETROARCH_CONFIG_DIR / 'retroarch.cfg'
MODIFIED_RA_CONFIG = RETROARCH_CONFIG_DIR / 'retroarch-modified.cfg'

FLIPS_BIN = '/usr/bin/flips'
CLEAN_ROM = 'cleansmw.sfc'