from pathlib import Path
import platform
BASE_DIR = Path(__file__).resolve().parent.parent
USER_HOME = Path.home()


####################################################################
#                                     Are These Paths Okay With You?
####################################################################

# The script should try to find these paths for you.
# If it fails or if you'd prefer to specify a different path, 
# # you can.

# RetroArch Binary
# If you change the path, do it like this: ( r'C:\different\path\retroarch.exe' )
# the "r" is required on Windows.
RETROARCH_BIN = r'C:\RetroArch-Win64\retroarch.exe'

# Floating IPS Binary
FLIPS_BIN = ''

# RA Config Directory
RETROARCH_CONFIG_DIR = r'C:\RetroArch-Win64'

# RA SNES Core
# Leave the .so (Linux) or .dll (Windows) off.
SNES_CORE = 'cores/snes9x_libretro'


#####################################################################
#                                                        Okay, Great!
#####################################################################

























# Just Leave These Alone
# Just Leave These Alone
# Just Leave These Alone
# Just Leave These Alone
# Just Leave These Alone
# Just Leave These Alone
# Just Leave These Alone





if platform.system() != "Windows":
    SNES_CORE = SNES_CORE + ".so"
else:
    SNES_CORE = SNES_CORE + ".dll"


DEFAULT_RA_CONFIG  = 'retroarch.cfg'            # RA Default Config
MODIFIED_RA_CONFIG = 'retroarch-modified.cfg'  # Save location for copy of default 
                                               # config used for options like --no-rewind
# Temp Paths
TMP_PATH      =  BASE_DIR / 'tmp'         # These Directories Will Be Deleted After Scrape
ZIPS_DL_PATH    =  TMP_PATH / 'zips'    # Used To Store Downloaded Zips During Scrape Phase
UNZIP_DL_PATH   =  TMP_PATH / 'unzip'  # Used to Store Unzipped Files During ROM Patch Phase
BPS_PATH        =  TMP_PATH / 'bps'         # Used to Store BPS patches pulled from Unzipped Archives

# Storage Paths
SQLITE_DB_FILE    = BASE_DIR / 'smwc.db'     # The sqlite3 Database
ROMS_DIR          = BASE_DIR / 'roms'       # Storage of clean rom and romhacks
CLEAN_ROM_DIR       = ROMS_DIR / 'clean'    # Directory Where Vanilla SMW .sfc file goes.
ROMHACKS_DIR        = ROMS_DIR / 'hacks'       # Directory to Store Romhacks

# Developer Options
# Just Leave These Alone
DEBUG_SCRAPER = {
    "ONE_PAGE_ONLY": True,         # If True, Scrapes Every Hack From Only One Page
    "ONE_HACK_ONLY": False,         # If True, Scrapes One Hack Only From Every Page,
                                    # If Both Options True, Scrapes One Hack From One Page
    "SKIP_DATABASE_INSERT": False,
    "SKIP_DOWNLOAD": False
}

VENDOR_FLIPS_DIR = BASE_DIR / 'vendor/flips'
VENDOR_FLIPS_BIN    = (VENDOR_FLIPS_DIR / 'flips') if platform.system() != 'Windows' else (VENDOR_FLIPS_DIR / 'flips.exe')