from random import choice
from typing import List, Tuple
import subprocess
import argparse
import sys
from pathlib import Path
import shutil

from .database import SMWCentralDatabase
from .scraper import SMWCentralScraper
from .romhack import SMWRomhack
from .config import RETROARCH_BIN, SNES_CORE, DEFAULT_RA_CONFIG, MODIFIED_RA_CONFIG

def scrape():
    scraper = SMWCentralScraper()
    db.write_records(scraper.records)

def random_hack(rating_threshold: float, type_substr: str):
    hacks: List[dict] = db.select_hacks_by_rating_type(
        'smwc/sql/select_hacks_by_rating_type.sql',
        rating_threshold=rating_threshold,
        type_substr=type_substr
    )

    try:
        pick: dict = choice(hacks)
    except IndexError as e:
        print(e)
        sys.exit()

    print(f"ID: {pick['id']}")
    print(f"Title: {pick['title']}")
    print(f"Created On: {pick['created_on']}")
    print(f"Page URL: {pick['page_url']}")
    print(f"Is Demo: {pick['is_demo']}")
    print(f"Is Featured: {pick['is_featured']}")
    print(f"Exit Count: {pick['exit_count']}")
    print(f"Rating: {pick['rating']}")
    print(f"Size: {pick['size']} {pick['size_units']}")
    print(f"Download Count: {pick['downloaded_count']}")
    print(f"Type: {pick['hack_type']}")
    print(f"Path: {pick['path']}")
    print(f"Author: {pick['author']}")
    launch_in_retroarch(pick['path'])


def _modify_retroarch_config(mod: List[Tuple]):
    if MODIFIED_RA_CONFIG.exists():
        MODIFIED_RA_CONFIG.unlink()

    with DEFAULT_RA_CONFIG.open() as rfo:
        cfg_text = rfo.read()

    modified_cfg_text = cfg_text.replace(mod[0], mod[1])

    with MODIFIED_RA_CONFIG.open('w') as wfo:
        wfo.write(modified_cfg_text)
        
def launch_in_retroarch(sfc: str) -> None:

    def modify(old: str, new: str, subprocess_cmd: List[str]) -> None:
        _modify_retroarch_config((old, new))
        for additional_arg in ['-c', MODIFIED_RA_CONFIG]:
            subprocess_cmd.append(additional_arg)
        return subprocess_cmd

    cmd: List = [RETROARCH_BIN, '-L', SNES_CORE, sfc]

    rewind = True if args.rewind else False if args.no_rewind else None

    if rewind:
        cmd = modify('rewind_enable = "false"',
                     'rewind_enable = "true"', cmd)
        
    if not rewind and rewind is not None:
        cmd = modify('rewind_enable = "true"',
                     'rewind_enable = "false"', cmd)

    subprocess.run(cmd)

db = SMWCentralDatabase('smwcentral.db')
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--scrape', 
        action='store_true', 
        help='Scrape SMWCentral and Build Database of Patched Romhacks'
    )
    parser.add_argument(
        '--random', 
        action='store_true', 
        help='Choose a random SMW hack and launch in RetroArch')
    parser.add_argument(
        '--type',
        type=str,
        help='Substring to match against hack types to include (e.g., "Easy", "Kaizo"); Use with --random'
    )
    parser.add_argument(
        '--rating',
        type=float,
        help='Minimum rating for a hack to be considered (e.g., 4.5); Use with --random'
    )

    rewind_options = parser.add_mutually_exclusive_group(required=False)
    rewind_options.add_argument(
        '--rewind',
        action='store_true',
        help='When launching Retroarch, enable rewind support. The default option is determined by your RA config.'
    )
    rewind_options.add_argument(
        '--no-rewind',
        action='store_true',
        help='When launching Retroarch, disable rewind support. The default option is determined by your RA config.'
    )
    args = parser.parse_args()



    if args.scrape:
        scrape()

    if args.random:
        type_substr = '' if args.type is None else args.type
        rating_threshold = -0.1 if args.rating is None else args.rating
        random_hack(rating_threshold=rating_threshold, type_substr=type_substr)
        


test_sfc_file = db.select_hack_by_id(208)[0]['path']