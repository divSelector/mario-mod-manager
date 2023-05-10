from random import choice
from typing import List, Optional, Dict, Tuple
from argparse import ArgumentParser, Namespace
import sys
import urwid

from smwc import db
from .database import SMWCentralDatabase
from .scraper import SMWCentralScraper
from .downloader import SMWRomhackDownloader
from .romhack import SMWRomhack
from .config import DEBUG_SCRAPER, SQLITE_DB_FILE, BASE_DIR
from .utils import get_clean_rom_path
from .tui import SMWRomhackSelection

class SMWCommandLineInterface:

    PROG: str = 'smwcentral.py'
    DESCRIPTION: str = """
        smwcentral.net scraper, downloader, database, romhack patcher and launcher\n
        by divselector
    """
    EPILOG: str = ""

    def __init__(self) -> None:

        def _get_queryset_call() -> Tuple[List[Dict[str, str]], Dict[str, str]]:
            return self.get_queryset(
                self.args.title, self.args.type, self.args.author, self.args.rating_over, 
                self.args.rating_under, self.args.exits_over, self.args.exits_under, 
                self.args.downloads_over, self.args.downloads_under,self.args.date_after, 
                self.args.date_before, self.args.featured, self.args.demo, rewind
            )


        self.scraper: Optional[SMWCentralScraper] = None
        self.downloader: Optional[SMWRomhackDownloader] = None
        
        self.args: Namespace = self.parse_args()
        
        if self.args.scrape:
            self.scrape()

        rewind = True if self.args.rewind else False if self.args.no_rewind else None
        if self.args._id:
            self.play_hack_with_id(self.args._id, rewind)

        elif self.args.random:
            hacks, options = _get_queryset_call()
            self.play_random_hack(hacks, options)
            
        if self.args.show_beaten:
            self.show_exits_cleared(beaten=True)


        if self.args.list:
            hacks, options = _get_queryset_call()
            self.list_hacks(hacks, options)
        

        if self.args.show_started:
            self.show_exits_cleared()

        
            
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
        top_level_options.add_argument('--list', action='store_true', 
            help='Open text-based user interface to select hack from query'
        )
        top_level_options.add_argument('--id', type=int, default=None, metavar='X', dest='_id',
            help='Launch a specific hack by ID number. Ignores --random and query options.'
        )

        # Query Options
        query_options = parser.add_argument_group("Query Modifiers (use these with --random or --list)")
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
            help='Display hacks in database where all exits are cleared.'
        )
        info_options.add_argument('--show-started', action='store_true', 
            help='Display hacks in database where any exits are marked cleared.'
        )

        return parser.parse_args()

    def scrape(self) -> None:
        clean_smw = get_clean_rom_path()

        self.scraper = SMWCentralScraper()
        self.scraper.scrape()
        
        if not DEBUG_SCRAPER['SKIP_DOWNLOAD'] and clean_smw is not None:
            self.downloader = SMWRomhackDownloader(self.scraper.records, {
                'batch_size': 10, 'batch_delay': 8, 'download_delay': 3, 
                'timeout': 60, 'max_retries': 3
            }, clean_smw)
            
        if not DEBUG_SCRAPER['SKIP_DATABASE_INSERT']:
            db.write_records(self.scraper.records)

            if self.downloader is not None and self.downloader.failures['badzip']:
                print("Removing records without paths to an SFC file...")
                db.execute(
                    db.read(BASE_DIR / 'smwc/sql/delete_hacks_where_null_path.sql'), sql_params=None
                )

    def get_queryset(self, title_substr: str, type_substr: str, author_substr: str, rating_gt: float, 
                         rating_lt: float, exits_gt: int, exits_lt: int, downloads_gt: int, 
                         downloads_lt: int, created_on_gt: str, created_on_lt: str, 
                         featured: str, demo: str, rewind: Optional[bool]=None) -> Tuple[List[dict], Dict]:
        
        hacks = db.select_hacks(title_substr, type_substr, author_substr, rating_gt, rating_lt, 
                                exits_gt, exits_lt, downloads_gt, downloads_lt, created_on_gt,
                                created_on_lt, featured, demo)
        
        return hacks, { 'rewind': rewind }

    def play_random_hack(self, hacks: List[Dict], opts: Dict) -> None:
        try:
            pick: dict = choice(hacks)
        except IndexError as e:
            print(e)
            sys.exit()
        self.print_record(pick)
        self.launch_hack(pick['path'][0], opts)


    def list_hacks(self, hacks: List[Dict], opts: Dict) -> None:
        urwid.MainLoop(SMWRomhackSelection(hacks), 
                       palette=[('reversed', 'standout', '')]).run()
        

    def play_hack_with_id(self, _id: int, rewind: Optional[bool]=None) -> None:
        hack = db.select_hack_by('id', _id)[0]
        self.print_record(hack)
        self.launch_hack(hack['path'][0], {'rewind': rewind})

    @staticmethod
    def launch_hack(path: str, opts: Dict) -> None:
        romhack = SMWRomhack(path)
        romhack.launch_in_retroarch(rewind=opts['rewind'])

    def show_exits_cleared(self, beaten: bool = False) -> None:
        if beaten:
            print("\nHACKS WITH ALL EXITS CLEARED:")
            results = db.select_without_params_from_file(
                'smwc/sql/select_hacks_beaten.sql'
            )
        else:
            print("\nHACKS WITH SOME EXITS CLEARED:")
            results = db.select_without_params_from_file(
                'smwc/sql/select_hacks_started.sql'
            )
        
        if results:
            for record in results:
                _id, title, total, cleared, *_ = record
                print(f"{_id}: {title} -- {cleared}/{total} Exits Clear!")
        else:
            
            print(f"\nYou haven't {'cleared' if beaten else 'started'} any yet... :(")
        print()


    @staticmethod
    def print_record(r: Dict[str, str]) -> None:
        print(''.join([
            f"ID:               {r['id']}\n",
            f"Title:            {r['title']}\n",
            f"Created On:       {r['created_on']}\n",
            f"Page URL:         {r['page_url']}\n",
            f"Is Demo:          {r['is_demo']}\n",
            f"Is Featured:      {r['is_featured']}\n",
            f"Exit Count:       {r['exit_count']}\n",
            f"Exits Cleared:    {r['exits_cleared']}\n",
            f"Rating:           {r['rating']}\n",
            f"Size:             {r['size']} {r['size_units']}\n",
            f"Download Count:   {r['downloaded_count']}\n",
            f"Type:             {r['hack_type']}\n",
            f"Path:             {r['path']}\n",
            f"Authors:          {r['author']}\n",
        ]))
        input("\nPRESS ENTER KEY TO START")


if __name__ == '__main__':
    app = SMWCommandLineInterface()
    db = SMWCentralDatabase(SQLITE_DB_FILE)
