from random import choice
from typing import List, Optional
import argparse
import sys

from .database import SMWCentralDatabase
from .scraper import SMWCentralScraper
from .romhack import SMWRomhack

def scrape():
    scraper = SMWCentralScraper()
    db.write_records(scraper.records)

def random_hack(title_substr: str, type_substr: str, author_substr: str, rating_gt: float, 
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="smwc.cli", description="""
        smwcentral.net scraper, downloader, database, romhack patcher and launcher
        by divselector
    """)

    top_level_options = parser.add_argument_group("Main Options")
    launch_options = parser.add_argument_group("Launch Options")

    # Scraper
    top_level_options.add_argument('--scrape', action='store_true', 
        help='Scrape SMWCentral and Build Database of Patched Romhacks'
    )

    # Random Select Arguments
    query_options = parser.add_argument_group("Query Modifiers (use these with --random)")
    top_level_options.add_argument('--random', action='store_true', 
        help='Choose a random SMW hack and launch in RetroArch')
    
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
    rewind_options = launch_options.add_mutually_exclusive_group(required=False)
    rewind_options.add_argument('--rewind', action='store_true',
        help='When launching Retroarch, enable rewind support. The default option is determined by your RA config.'
    )
    rewind_options.add_argument('--no-rewind', action='store_true',
        help='When launching Retroarch, disable rewind support. The default option is determined by your RA config.'
    )

    args = parser.parse_args()

    db = SMWCentralDatabase('smwcentral.db')

    if args.scrape:
        scrape()

    if args.random:
        rewind = True if args.rewind else False if args.no_rewind else None
        random_hack(args.title, args.type, args.author, args.rating_over, args.rating_under, 
                    args.exits_over, args.exits_under, args.downloads_over, args.downloads_under,
                    args.date_after, args.date_before, args.featured, args.demo, rewind)
