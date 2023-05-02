from random import choice
from typing import List
import subprocess
import argparse

from database import SMWCentralDatabase
from scraper import SMWCentralScraper
from config import RETROARCH_BIN, SNES_CORE

def scrape():
    scraper = SMWCentralScraper()
    db.open_database(
        db.write_records, 
        action_param=scraper.records
    )

def random_hack():
    hacks: List[dict] = db.select_hacks('sql/select_hacks.sql')
    pick: dict = choice(hacks)
    print(f"ID: {pick['id']}")
    print(f"Title: {pick['title']}")
    print(f"Path: {pick['path']}")
    print(f"Rating: {pick['rating']}")
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
        '--random-hack', 
        action='store_true', 
        help='Choose a random SMW hack and launch in RetroArch')
    args = parser.parse_args()

    if args.scrape:
        scrape()

    if args.random_hack:
        random_hack()


db = SMWCentralDatabase('smwcentral.db')
if __name__ == '__main__':
    main()