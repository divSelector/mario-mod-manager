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

def scrape():
    scraper = SMWCentralScraper()
    db.write_records(scraper.records)

def random_hack(rating_gt: float, type_substr: str, rewind: bool):
    hacks: List[dict] = db.select_hacks(
        rating_gt=rating_gt,
        type_substr=type_substr
    )

    try:
        pick: dict = choice(hacks)
    except IndexError as e:
        print(e)
        sys.exit()

    print_record(pick)

    romhack = SMWRomhack(pick['path'][0])
    romhack.launch_in_retroarch(rewind=rewind)


def print_record(r):
    print(f"ID: {r['id']}")
    print(f"Title: {r['title']}")
    print(f"Created On: {r['created_on']}")
    print(f"Page URL: {r['page_url']}")
    print(f"Is Demo: {r['is_demo']}")
    print(f"Is Featured: {r['is_featured']}")
    print(f"Exit Count: {r['exit_count']}")
    print(f"Rating: {r['rating']}")
    print(f"Size: {r['size']} {r['size_units']}")
    print(f"Download Count: {r['downloaded_count']}")
    print(f"Type: {r['hack_type']}")
    print(f"Path: {r['path']}")
    print(f"Author: {r['author']}")


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
        rating_gt = -0.1 if args.rating is None else args.rating
        type_substr = '' if args.type is None else args.type
        rewind = True if args.rewind else False if args.no_rewind else None
        random_hack(
            rating_gt=rating_gt, 
            type_substr=type_substr,
            rewind=rewind
        )
