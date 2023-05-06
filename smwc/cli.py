from random import choice
from typing import List, Optional, Dict
from argparse import ArgumentParser, Namespace
import sys

from smwc import db
from .database import SMWCentralDatabase
from .scraper import SMWCentralScraper
from .downloader import SMWRomhackDownloader
from .romhack import SMWRomhack
from .config import DEBUG_SCRAPER, SQLITE_DB_FILE, BASE_DIR

class SMWCommandLineInterface:

    PROG: str = "smwc.cli"
    DESCRIPTION: str = """
        smwcentral.net scraper, downloader, database, romhack patcher and launcher\n
        by divselector
    """
    EPILOG: str = ""

    def __init__(self):
        self.scraper: Optional[SMWCentralScraper] = None
        self.downloader: Optional[SMWRomhackDownloader] = None
        
        self.args: Namespace = self.parse_args()
        
        if self.args.scrape:
            self.scrape()

        rewind = True if self.args.rewind else False if self.args.no_rewind else None
        if self.args._id:
            self.play_hack_with_id(self.args._id, rewind)

        elif self.args.random:
            self.play_random_hack(self.args.title, self.args.type, self.args.author, self.args.rating_over, 
                                  self.args.rating_under, self.args.exits_over, self.args.exits_under, 
                                  self.args.downloads_over, self.args.downloads_under,self.args.date_after, 
                                  self.args.date_before, self.args.featured, self.args.demo, rewind)
            
        elif self.args.show_beaten:
            self.show_beaten()

            
    def parse_args(self) -> Namespace:
        parser = ArgumentParser(
            prog=SMWCommandLineInterface.PROG, 
            description=SMWCommandLineInterface.DESCRIPTION,
            epilog=SMWCommandLineInterface.EPILOG
        )

        top_level_options = parser.add_argument_group("Main Options")
        top_level_options.add_argument('--scrape', action='store_true', 
            help='Scrape SMWCentral and Build Database of Patched Romhacks'
        )
        top_level_options.add_argument('--random', action='store_true', 
            help='Choose a random SMW hack and launch in RetroArch'
        )
        top_level_options.add_argument('--id', type=int, default=None, metavar='X', dest='_id',
            help='Launch a specific hack by ID number. Ignores --random and query options.'
        )

        # Query Options
        query_options = parser.add_argument_group("Query Modifiers (use these with --random)")
        query_options.add_argument('--title', type=str, default='', metavar='X',
            help='Substring to match against hack titles to include (e.g., "Super", "World")'
        )
        query_options.add_argument('--type', type=str, default='', metavar='X',
            help='Substring to match against hack types to include (e.g., "Easy", "Kaizo")'
        )
        query_options.add_argument('--author', type=str, default='', metavar='X',
            help='Substring to match against hack authors to include (e.g., "NewPointless", "yeahman")'
        )
        query_options.add_argument('--rating-over', type=float, default=-0.1, metavar='X',
            help='Minimum rating for a hack to be considered (e.g., 4.5)'
        )
        query_options.add_argument('--rating-under', type=float, default=5.1, metavar='X',
            help='Maximum rating for a hack to be considered (e.g., 2.1)'
        )
        query_options.add_argument('--exits-over', type=int, default=0, metavar='X',
            help='Minimum exits for a hack to be considered (e.g., 10)'
        )
        query_options.add_argument('--exits-under', type=int, default=255, metavar='X',
            help='Maximum exits for a hack to be considered (e.g., 96)'
        )
        query_options.add_argument('--downloads-over', type=int, default=-1, metavar='X',
            help='Minimum times downloaded for a hack to be considered (e.g., -1)'
        )
        query_options.add_argument('--downloads-under', type=int, default=999999, metavar='X',
            help='Maximum times downloaded for a hack to be considered (e.g., 9999999)'
        )
        query_options.add_argument('--date-after', type=str, default='1999-08-24', metavar='X',
            help='Must be uploaded after this date for hack to be considered (e.g., 1999-08-24)'
        )
        query_options.add_argument('--date-before', type=str, default='2023-03-24', metavar='X',
            help='Must be uploaded before this date for hack to be considered (e.g., 2023-03-24)'
        )
        query_options.add_argument('--featured', type=str, default='', metavar='X',
            help='Use "Yes" or "No" to consider hacks marked as *featured* by smwentral.net'
        )
        query_options.add_argument('--demo', type=str, default='', metavar='X',
            help='Use "Yes" or "No" to consider hacks marked as demos'
        )
        
        # RetroArch Launch Arguments
        launch_options = parser.add_argument_group("Launch Options")
        rewind_options = launch_options.add_mutually_exclusive_group(required=False)
        rewind_options.add_argument('--rewind', action='store_true',
            help='When launching Retroarch, enable rewind support. The default option is determined by your RA config.'
        )
        rewind_options.add_argument('--no-rewind', action='store_true',
            help='When launching Retroarch, disable rewind support. The default option is determined by your RA config.'
        )

        info_options = parser.add_argument_group("Show Info Options")
        info_options.add_argument('--show-beaten', action='store_true', 
            help='Display hacks in database where all exits are cleared'
        )

        return parser.parse_args()

    def scrape(self):
        self.scraper = SMWCentralScraper()
        
        if not DEBUG_SCRAPER['SKIP_DOWNLOAD']:
            self.downloader = SMWRomhackDownloader(self.scraper.records, {
                'batch_size': 10, 'batch_delay': 8, 'download_delay': 3, 
                'timeout': 60, 'max_retries': 3
            })
            
        if not DEBUG_SCRAPER['SKIP_DATABASE_INSERT']:
            db.write_records(self.scraper.records)

            if self.downloader.failures['badzip']:
                print("Removing records without paths to an SFC file...")
                db.execute(
                    db.read(BASE_DIR / 'smwc/sql/delete_hacks_where_null_path.sql')
                )

    def play_random_hack(self, title_substr: str, type_substr: str, author_substr: str, rating_gt: float, 
                         rating_lt: float, exits_gt: int, exits_lt: int, downloads_gt: int, 
                         downloads_lt: int, created_on_gt: str, created_on_lt: str, 
                         featured: str, demo: str, rewind: Optional[bool]=None):
        hacks: List[dict] = db.select_hacks(title_substr, type_substr, author_substr, rating_gt, rating_lt, 
                                exits_gt, exits_lt, downloads_gt, downloads_lt, created_on_gt,
                                created_on_lt, featured, demo)

        try:
            pick: dict = choice(hacks)
        except IndexError as e:
            print(e)
            sys.exit()

        self.print_record(pick)
        self.launch_hack(pick['path'][0], {'rewind': rewind})
        

    def play_hack_with_id(self, _id: int, rewind: Optional[bool]=None):
        hack = db.select_hack_by('id', _id)[0]
        self.print_record(hack)
        self.launch_hack(hack['path'][0], {'rewind': rewind})

    @staticmethod
    def launch_hack(path: str, opts: Dict):
        romhack = SMWRomhack(path)
        romhack.launch_in_retroarch(rewind=opts['rewind'])

    def show_beaten(self):
        print("\nHACKS WITH ALL EXITS CLEARED:")
        results = db.select_hacks_beaten()
        if results:
            for record in results:
                _id, title, cleared, _, _ = record
                print(f"{_id}: {title} -- {cleared} Exits Clear!")
        else:
            print("\nYou haven't cleared any hacks yet... :(")
        print()


    @staticmethod
    def print_record(r):
        print(f"ID: {r['id']}")
        print(f"Title: {r['title']}")
        print(f"Created On: {r['created_on']}")
        print(f"Page URL: {r['page_url']}")
        print(f"Is Demo: {r['is_demo']}")
        print(f"Is Featured: {r['is_featured']}")
        print(f"Exit Count: {r['exit_count']}")
        print(f"Exits Cleared: {r['exits_cleared']}")
        print(f"Rating: {r['rating']}")
        print(f"Size: {r['size']} {r['size_units']}")
        print(f"Download Count: {r['downloaded_count']}")
        print(f"Type: {r['hack_type']}")
        print(f"Path: {r['path']}")
        print(f"Author: {r['author']}")


if __name__ == '__main__':
    app = SMWCommandLineInterface()
    db = SMWCentralDatabase(SQLITE_DB_FILE)
