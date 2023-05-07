from typing import List, Dict, Tuple, Sequence, Optional
from pathlib import Path
import requests
import shutil
import zipfile
import zlib
import platform
import subprocess
from datetime import datetime
import time
import string
import sys

from .config import (
    ZIPS_DL_PATH, 
    UNZIP_DL_PATH, 
    BPS_PATH, 
    FLIPS_BIN, 
    TMP_PATH,
    BASE_DIR,
    ROMHACKS_DIR,
    VENDOR_FLIPS_BIN
)
from .utils import get_bin

class SMWRomhackDownloader:


    def __init__(self, records: List[Dict], opts: Dict, clean_rom: Path) -> None:
        self.flips: Optional[Path] = self.find_flips()
        if self.flips is None:
            print("Cannot find flips... please install it")
            print("https://github.com/Alcaro/Flips")
            sys.exit()
        self.clean_rom = clean_rom
        self.records: List[Dict] = records
        self.failures: Dict[str, List] = { 'http': [],
                                           'badzip': [],
                                           'timeout': [] }
        
        self.batch_size: int = opts['batch_size']
        self.batch_delay: int = opts['batch_delay']        # seconds
        self.download_delay: int = opts['download_delay']  # seconds
        self.timeout: int = opts['timeout']                # seconds
        self.max_retries: int = opts['max_retries']

        self.batches: List[List[Dict]] = self.enqueue_batches(self.records)

        self.make_temp_dirs([ZIPS_DL_PATH, 
                             UNZIP_DL_PATH, 
                             BPS_PATH])
        
        record_to_zip_pairs = self.download_batches()

        for record, zip_file in record_to_zip_pairs:
            sfc_files = self.unzip(zip_file)
            record['sfc_files'] = sfc_files
            try:
                shutil.rmtree(UNZIP_DL_PATH)
            except FileNotFoundError:
                pass

        shutil.rmtree(TMP_PATH)

    def enqueue_batches(self, records: List[Dict]) -> List[List[Dict]]:
        """
        Take a list of records and divide them into a nested list of lists to process in batches.
        """
        return [records[i:i+self.batch_size] 
                for i in range(0, len(records), self.batch_size)]

    def make_temp_dirs(self, dirs: List[Path]) -> None:
        """
        Create temp directories if they do not exist
        """
        # Create Paths if they do not exist
        for path in dirs:
            if not path.exists():
                path.mkdir(exist_ok=True, parents=True)


    def download_batches(self) -> List[Tuple[Dict, Path]]:
        """
        This is just a basic way of implementing some self-imposed restraint and
        ratelimiting while downloading so much from the server at once.
        Most of the function is just informing the user about the state of the process. 
        """
        records: List = [] 
        for b_idx, batch in enumerate(self.batches):
            print(f"[{b_idx}/{len(self.batches)}] Downloading batch of {len(batch)} archives...")

            for u_idx, record in enumerate(batch):
                url = record['download_url']
                print(f"[{u_idx}/{len(batch)}] Downloading archive from {url}...")

                self.make_temp_dirs([UNZIP_DL_PATH])
                zip_file = self.download_zip(url)

                records.append((record, zip_file))

                print(f"Waiting {self.download_delay} second(s) till next download...")
                print()
                time.sleep(self.download_delay)

            print(f"Waiting {self.batch_delay} second(s) to start next batch of downloads...")
            time.sleep(self.batch_delay)

        print("Downloading batches complete")
        return records

      

    def download_zip(self, url: str) -> Path:
        """
        Handles making the request and dealing with failures.
        """
        # Make Request
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status() 
                break  # Break out of the retry loop if the request succeeded
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    # If this is the last retry attempt, 
                    # raise the Timeout exception to the caller
                    print(f"Exceeded max retries. Failed to Download {url}")
                    self.failures['timeout'].append(url)
                else:
                    # If there are more retry attempts remaining, 
                    # wait for the specified delay and try again
                    time.sleep(self.batch_delay)
            except requests.exceptions.HTTPError:
                print(f"Received a {response.status_code} from server and failed on {url}")
                self.failures['http'].append(url)

        filename: str = self.get_filename_from_url(url)
        output_path: Path = ZIPS_DL_PATH / filename
        with output_path.open("wb") as fo:
            fo.write(response.content)

        print(f"File saved as {output_path}")
        return output_path
    

    @staticmethod
    def get_filename_from_url(url: str) -> str:
        """
        Derive a useful local filename based on URL encoded filename on a server.
        Remove obnoxious characters where possible.
        """
        filename: str = Path(url).name

        # Start with all special characters and remove those that are useful in filenames
        special_chars: str = string.punctuation
        for old_char, new_char in [('_', ''), ('-', ''), ('.', '')]:
            special_chars = special_chars.replace(old_char, new_char)

        # Replace URL encoded spaces with underscores and remove all characters defined above
        replace_chars: Sequence[Tuple] = [('%20', '_')] + [(c, '') for c in special_chars]
        for old_char, new_char in replace_chars:
            filename = filename.replace(old_char, new_char)

        return filename


    def unzip(self, zip_path: Path) -> List[str]:
        """
        Unzip a single file and log failures.
        """
        self.make_temp_dirs([UNZIP_DL_PATH])
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip:
                print()
                print(f"Unzipping {zip_path}...")
                zip.extractall(UNZIP_DL_PATH)
        except (zipfile.BadZipFile, zlib.error) as e:
            print(f"Failure unzipping {zip_path}: {e}")
            self.failures['badzip'].append(zip_path)

        sfc_files: List[str] = self.handle_patches()
        return sfc_files


    def handle_patches(self) -> List[str]:
        """
        Glob up all bps and ips patch files in the unzip tmp dir
        Move them to the bps directory. Once Moved, output sfc files for
        each patch.
        """
        # Move the patches to the patch directory
        patches: List = []
        sfc_files: List = []
        for ext in ['bps', 'ips']:
            for patch in UNZIP_DL_PATH.glob(f'**/*.{ext}'):
                new_patch_filename: str = patch.name.replace(' ', '_')
                patch_move_path = BPS_PATH / new_patch_filename
                print(f"Moving {patch.relative_to(BASE_DIR)} to "+\
                      f"{patch_move_path.relative_to(BASE_DIR)}")
                patch.replace(patch_move_path)
                patches.append(patch_move_path)

        # Output an SFC ROM for each patch.
        for patch in patches:
            sfc = self.apply_patch(patch)
            sfc_files.append(str(sfc))

        return sfc_files
    

    def apply_patch(self, patch: Path) -> Path:
        """
        Makes the sfc directory if it does not exist. Formats a filename with
        a timestamp to avoid overwriting similar filenames.
        Locate the Floating IPS binary and run it on the clean vanilla SMW rom.
        """
        ROMHACKS_DIR.mkdir(parents=True, exist_ok=True)

        sfc_file_suffix: str = f"-{datetime.now().strftime('%Y%m%d%H%M%S')}.sfc"
        sfc_path: Path = ROMHACKS_DIR / (patch.stem + sfc_file_suffix)

        print("Executing flips to patch romhack...")
        flips_bin = SMWRomhackDownloader.flips_bin
        subprocess.run([str(flips_bin), '-a', str(patch), str(self.clean_rom), str(sfc_path)])

        return sfc_path.relative_to(ROMHACKS_DIR)

    def find_flips(self) -> Optional[Path]:
        flips_bin = get_bin(
            FLIPS_BIN, 
            which_cmd_name='flips', 
            version_output_substrings=['floating', 'flips']
        )
        if flips_bin is None and VENDOR_FLIPS_BIN.exists():
            print("Looking for flips in vendor directory... this version could be outdated.")
            flips_bin = get_bin(
                VENDOR_FLIPS_BIN, 
                which_cmd_name='', 
                version_output_substrings=['']
            )
            if flips_bin is not None:
                print(f"Found {flips_bin}!!!")
        return flips_bin