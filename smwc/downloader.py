from typing import List, Dict, Tuple
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

from .config import (
    ZIPS_DL_PATH, 
    UNZIP_DL_PATH, 
    BPS_PATH, 
    FLIPS_BIN, 
    CLEAN_ROM,
    SFC_DIR,
    TMP_PATH
)
from .utils import get_bin

class SMWRomhackDownloader:

    def __init__(self, records: List[Dict], opts: Dict = {
        'batch_size': 10, 
        'batch_delay': 1, 
        'download_delay': 0, 
        'timeout': 60,
        'max_retries': 3
    }) -> None:
        self.records: List[Dict] = records
        self.failures = { 'http': [],
                          'badzip': [],
                          'timeout': [] }
        
        self.batch_size: int = opts['batch_size']
        self.batch_delay: int = opts['batch_delay']        # seconds
        self.download_delay: int = opts['download_delay']  # seconds
        self.timeout: int = opts['timeout']                # seconds
        self.max_retries: int = opts['max_retries']

        self.batches: List[List[Dict]] = self.enqueue_batches(self.records)

        self.make_temp_dirs()
        self.download_batches()
        shutil.rmtree(TMP_PATH)

    def enqueue_batches(self, records: List[Dict]) -> List[List[Dict]]:
        """
        Take a list of records and divide them into a nested list of lists to process in batches.
        """
        return [records[i:i+self.batch_size] 
                for i in range(0, len(records), self.batch_size)]

    def make_temp_dirs(self):
        """
        Create temp directories if they do not exist
        """
        # Create Paths if they do not exist
        for path in [ZIPS_DL_PATH, UNZIP_DL_PATH, BPS_PATH]:
            if not path.exists():
                path.mkdir(exist_ok=True, parents=True)


    def download_batches(self):
        """
        This is just a basic way of implementing some self-imposed restraint and
        ratelimiting while downloading so much from the server at once.
        Most of the function is just informing the user about the state of the process. 
        """
        for b_idx, batch in enumerate(self.batches):
            print(f"[{b_idx}/{len(self.batches)}] Downloading batch of {self.batch_size} archives...")

            for u_idx, record in enumerate(batch):
                url = record['download_url']
                print(f"[{u_idx}/{len(batch)}] Downloading archive from {url}...")

                self.make_temp_dirs()
                zip_file = self.download_zip(url)
                sfc_files = self.unzip(zip_file)
                record['sfc_files'] = sfc_files
                shutil.rmtree(UNZIP_DL_PATH)


                print(f"Waiting {self.download_delay} second(s) till next download...")
                time.sleep(self.download_delay)

            print(f"Waiting {self.batch_delay} second(s) to start next batch of downloads...")
            time.sleep(self.batch_delay)
        print("Scraping batches complete")
      

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
        replace_chars: List[Tuple] = [('%20', '_')] + [(c, '') for c in special_chars]
        for old_char, new_char in replace_chars:
            filename = filename.replace(old_char, new_char)

        return filename


    def unzip(self, zip_path: Path):
        """
        Unzip a single file and log failures.
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip:
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
                print(f"Moving {patch} to {patch_move_path}")
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
        SFC_DIR.mkdir(parents=True, exist_ok=True)
        if platform.system() != 'Windows':
            sfc_file_suffix: str = f"-{datetime.now().strftime('%Y%m%d%H%M%S')}.sfc"
            sfc_path: Path = SFC_DIR / (patch.stem + sfc_file_suffix)

            print("Executing flips to patch romhack...")
            flips_bin = get_bin(
                FLIPS_BIN, 
                which_cmd_name='flips', 
                version_output_substrings=['floating', 'flips']
            )

            subprocess.run([flips_bin, '-a', patch, CLEAN_ROM, sfc_path])

            return sfc_path
