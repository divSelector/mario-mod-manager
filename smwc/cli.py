from random import choice
from typing import List
import subprocess
import argparse
import sys

from .database import SMWCentralDatabase
from .scraper import SMWCentralScraper
from .config import RETROARCH_BIN, SNES_CORE

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


def launch_in_retroarch(sfc: str):
    subprocess.run([RETROARCH_BIN, '-L', SNES_CORE, sfc])

def main():
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
    args = parser.parse_args()

    if args.scrape:
        scrape()

    if args.random:
        type_substr = '' if args.type is None else args.type
        rating_threshold = -0.1 if args.rating is None else args.rating
        random_hack(rating_threshold=rating_threshold, type_substr=type_substr)
        


db = SMWCentralDatabase('smwcentral.db')
if __name__ == '__main__':
    main()