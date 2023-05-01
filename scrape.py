from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Callable, Optional
import requests
import sys
from pathlib import Path
import sqlite3
import zipfile
import platform
import subprocess
from datetime import datetime
import shutil
import zlib

TMP_PATH = Path('tmp')
ZIPS_DL_PATH = TMP_PATH / 'zips'
ZIP_DL_PATH = TMP_PATH / 'tmp'
BPS_PATH = TMP_PATH / 'bps'
FLIPS_BIN = '/usr/bin/flips'
CLEAN_ROM = 'cleansmw.sfc'

class SMWCentralScraper:
    HACKS_URL = "https://www.smwcentral.net/?p=section&s=smwhacks&o=rating"
    def __init__(self) -> None:
        self.test = None
        self.hacks_url = SMWCentralScraper.HACKS_URL
        self.hacks_total: int = self.get_hack_pages_count()
        self.hack_pages_urls: list = self.get_hack_pages_urls(self.hacks_url)
        self.records = self.flatten(self.scrape_all_pages())

    def get_page_content(self, page: str) -> str:
        print(f"Requesting page: {page}")
        res = requests.get(page)
        res.raise_for_status()
        return res.content
    
    def get_content_soup(self, content: str) -> BeautifulSoup:
        return BeautifulSoup(content, "html.parser")
    
    def get_hack_pages_count(self) -> int:
        content: str = self.get_page_content(self.hacks_url)
        soup: BeautifulSoup = self.get_content_soup(content)
        last_page: str = soup.select_one('ul.page-list li:last-child')
        try:
            return int(last_page.string)
        except ValueError:
            print(f"{last_page.string} is not a number.")
            sys.exit()

    def get_hack_pages_urls(self, base_url: str):
        urls: list = []
        for page_number in range(1, self.hacks_total+1):
            urls.append(base_url + f"&n={page_number}")
        return urls
    
    def scrape_all_pages(self) -> None:
        total_hacks_on_all_pages: List[dict] = []

        for url in self.hack_pages_urls:
            total_hacks_on_all_pages.append(self.scrape_hacks_list_page(url))
        # total_hacks_on_all_pages.append(self.scrape_hacks_list_page(self.hack_pages_urls[0]))

        return total_hacks_on_all_pages

    def scrape_hacks_list_page(self, url: str) -> List[dict]:
        total_hacks_on_page: List[dict] = []
        content: str = self.get_page_content(url)
        page_soup: BeautifulSoup = self.get_content_soup(content)
        page_row_tags: List[Tag] = page_soup.select('table.list tbody tr')

        for row in page_row_tags:
            total_hacks_on_page.append(self.scrape_row_from_hacks_list(row))
        # self.scrape_row_from_hacks_list(page_row_tags[11])

        return total_hacks_on_page

    def scrape_row_from_hacks_list(self, row: Tag) -> dict:
        hack_title: str = self.scrape_title_from_row(row)
        hack_page_url: str = self.scrape_url_from_row(row)
        hack_is_demo: str = row.find_all('td')[1].string
        hack_is_featured: str = row.find_all('td')[2].string
        hack_exit_count: str = row.find_all('td')[3].string.split()[0]
        hack_types: list = row.find_all('td')[4].string.split(', ')
        hack_authors: list = [
            author.string for author in row.find_all('td')[5].select('a')
        ]
        hack_rating: float = self.scrape_rating_from_row(row)
        hack_size: dict = {
            'value': row.find_all('td')[7].string.split('\xa0')[0],
            'units': row.find_all('td')[7].string.split('\xa0')[1]
        }
        hack_download_url: str = "https:" + row.find_all('td')[8].select_one('a')['href']
        hack_total_downloads: str = row.find_all('td')[8].select_one('span.secondary-info').string.split()[0].replace(',', '')

        record = {
            "title": hack_title,
            "page_url": hack_page_url,
            "is_demo": hack_is_demo,
            "is_featured": hack_is_featured,
            "exit_count": hack_exit_count,
            "types": hack_types,
            "authors": hack_authors,
            "rating": hack_rating,
            "size": hack_size,
            "download_url": hack_download_url,
            "downloaded_count": hack_total_downloads,
            "sfc_files": []
        }

        zip_path: Path = self.download_zip(record["download_url"])
        bps_paths: List[Path] = self.unzip_for_bps(zip_path)

        sfc_files: List = []

        # Apply the patch to the bps files
        for bps_file in bps_paths:
            sfc_files.append(self.apply_patch(bps_file))

        # Add SFC file paths to record dict
        for sfc in sfc_files:
            record['sfc_files'].append(sfc)

        # Remove BPS Files After Patching
        for bps_file in bps_paths:
            try:
                bps_file.unlink()
            except FileNotFoundError:
                pass
        
        return record

    @staticmethod
    def scrape_url_from_row(row: Tag) -> str:
        base = "https://www.smwcentral.net"
        return base + row.select_one('td.text a')['href']

    @staticmethod
    def scrape_title_from_row(row: Tag) -> str:
        return row.select_one('td.text a').string

    @staticmethod
    def scrape_upload_time_from_row(row: Tag) -> str:
        return row.select_one('time')['datetime']

    @staticmethod
    def scrape_rating_from_row(row: Tag) -> float:
        rating = row.find_all('td')[6].string
        try:
            return float(rating)
        except ValueError:
            return 0.0
        
    @staticmethod
    def flatten(array: List) -> List:
        return [item for sublist in array for item in sublist]
    
    def download_zip(self, url: str) -> Path:
        zips_path: Path = ZIPS_DL_PATH
        tmp_path: Path = ZIP_DL_PATH
        # Create Paths if they do not exist
        for path in [zips_path, tmp_path]:
            if not path.exists():
                path.mkdir(exist_ok=True, parents=True)
        # Empty Temp Directory
        shutil.rmtree(tmp_path)


        filename: str = Path(url).name.replace("%20", "_").replace('%', '')

        res = requests.get(url)
        res.raise_for_status()

        output_path: Path = zips_path / filename
        with open(output_path, "wb") as f:
            f.write(res.content)
        print("File saved as {}".format(output_path))

        return output_path
    
    def unzip_for_bps(self, zip_path: Path) -> Path:
        tmp_path: Path = ZIP_DL_PATH
        bps_dir: Path = BPS_PATH
        if not bps_dir.exists():
            bps_dir.mkdir(parents=True, exist_ok=True)

        print(f"Unzipping to {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip:
                zip.extractall(tmp_path)
        except zipfile.BadZipFile:
            print(f"BadZipFile: {zip_path}")
        except zlib.error as e:
            print(f"zlib.error: {e}")


        bps_files = []
        for bps_file in tmp_path.glob('**/*.bps'):
            new_bps_filename = bps_file.name.replace(' ', '_')
            bps_move_path = bps_dir / new_bps_filename
            print(f"Moving {bps_file} to {bps_move_path}")
            bps_file.replace(bps_move_path)
            bps_files.append(bps_move_path)

        return bps_files
        
    def apply_patch(self, bps: Path) -> Path:   
        if platform.system() != 'Windows':
            output_dir = 'sfc'
            if not Path(output_dir).exists():
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            sfc_path = f"{output_dir}/{bps.stem}-{datetime.now().strftime('%Y%m%d%H%M%S')}.sfc"
            print("Executing flips to patch romhack")
            subprocess.run([FLIPS_BIN, '-a', bps, CLEAN_ROM, sfc_path])
            return sfc_path



class SMWCentralDatabase:
    def __init__(self, db_path: str) -> None:
        self.db: Path = Path(db_path)
        if not self.db.exists():
            self.open_database(self.create_tables)
        else:
            print(f"Database Found at {self.db}")

    def open_database(self, action: Callable, action_param: Optional[List] = None) -> None:
        print(f"Opening Database Connection at {self.db}")
        with sqlite3.connect(self.db) as conn:
            action(conn) if action_param is None else action(conn, action_param)
        print(f"Closing Database Connection at {self.db}")

    def create_tables(self, conn: sqlite3.Connection, **kwargs):
        print(f"Creating TABLE hacks")
        conn.execute('''
        CREATE TABLE hacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            page_url TEXT NOT NULL UNIQUE,
            is_demo TEXT NOT NULL,
            is_featured TEXT NOT NULL,
            exit_count INTEGER NOT NULL,
            rating REAL NOT NULL,
            size REAL NOT NULL,
            size_units TEXT NOT NULL,
            download_url TEXT NOT NULL,
            downloaded_count INTEGER NOT NULL
            );
        ''') 
        print(f"Creating TABLE hack_types")
        conn.execute('''
            CREATE TABLE hack_types (
                hack_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
            );
        ''')
        print(f"Creating TABLE hack_authors")
        conn.execute('''
            CREATE TABLE hack_authors (
                hack_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
            );
        ''')
        print(f"Creating TABLE hack_paths")
        conn.execute('''
            CREATE TABLE hack_paths (
                hack_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
            );
        ''')
        conn.commit()

    def write_records(self, conn: sqlite3.Connection, records: List[dict] = []) -> None:
        print(f"Preparing to write {len(records)} records")
        for record in records:
            prepared_record: tuple = self.prepare_hack_record_for_db(record)
            c = conn.cursor()
            print(f"Inserting record for {record['title']} to hacks")
            c.execute("INSERT INTO hacks (title, page_url, is_demo, is_featured, exit_count, rating, size, size_units, "+\
                        "download_url, downloaded_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", prepared_record)
            hack_id = c.lastrowid

            print(f"Inserting record for {record['title']} to hack_authors")
            for author in record['authors']:
                c.execute("INSERT INTO hack_authors (hack_id, author) VALUES (?, ?)", (hack_id, author))

            print(f"Inserting record for {record['title']} to hack_types")
            for hack_type in record['types']:
                c.execute("INSERT INTO hack_types (hack_id, type) VALUES (?, ?)", (hack_id, hack_type))

            print(f"Inserting record for {record['title']} to hack_paths")
            for hack_path in record['sfc_files']:
                c.execute("INSERT INTO hack_paths (hack_id, path) VALUES (?, ?)", (hack_id, hack_path))
            
            print(f"Committing record for {record['title']}")
            conn.commit()
            print()

    @staticmethod
    def prepare_hack_record_for_db(hack: dict) -> tuple:
        return (
            hack['title'], 
            hack['page_url'], 
            hack['is_demo'], 
            hack['is_featured'], 
            hack['exit_count'], 
            hack['rating'], 
            hack['size']['value'], 
            hack['size']['units'], 
            hack['download_url'], 
            hack['downloaded_count']
        )


db = SMWCentralDatabase('smwcentral.db')

scraper = SMWCentralScraper()
db.open_database(
    db.write_records, 
    action_param=scraper.records
)