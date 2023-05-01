from random import choice
from typing import Callable
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

def select_random_from_query(query: Callable):
    return choice(query())

def launch_sfc_in_retroarch(sfc: str):
    subprocess.run([RETROARCH_BIN, '-L', SNES_CORE, sfc])



db = SMWCentralDatabase('smwcentral.db')
pick = select_random_from_query(
    db.query_standard_normal_rated_over_3_9
)
launch_sfc_in_retroarch(pick)
