from random import choice
from typing import List
import subprocess

from database import SMWCentralDatabase
from scraper import SMWCentralScraper
from config import RETROARCH_BIN, SNES_CORE

def scrape():
    scraper = SMWCentralScraper()
    db.open_database(
        db.write_records, 
        action_param=scraper.records
    )

def get_random_hack(hacks: List[dict]):
    pick = choice(hacks)
    print(f"ID: {pick['id']}")
    print(f"Title: {pick['title']}")
    print(f"Path: {pick['path']}")
    print(f"Rating: {pick['rating']}")
    return pick['path']

def launch_in_retroarch(sfc: str):
    subprocess.run([RETROARCH_BIN, '-L', SNES_CORE, sfc])



db = SMWCentralDatabase('smwcentral.db')
hacks = db.select_hacks('sql/select_hacks.sql')
hack_path = get_random_hack(hacks)
launch_in_retroarch(hack_path)
