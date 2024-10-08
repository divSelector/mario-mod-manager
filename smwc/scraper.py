from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List, Dict, Optional
import requests
import sys
from datetime import datetime

from smwc import db
from .config import *
from .utils import get_bin

class SMWCentralScraper:
    HACKS_URL = "https://www.smwcentral.net/?p=section&s=smwhacks"
    def __init__(self, url: Optional[str] = None) -> None:
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
        }
        self.hacks_url = url if url is not None else self.HACKS_URL
        self.hacks_page_content: str = self.get_page_content(self.hacks_url)


    def scrape(self) -> None:
        self.hack_pages_count: int = self.get_hack_pages_count(self.hacks_page_content)
        self.hack_pages_urls: list = self.get_hack_pages_urls(
            self.hacks_url
        )

        self.already_scraped = [
            record[-1] for record in db.select_without_params_from_file(
                'smwc/sql/select_hacks_already_scraped.sql'
            )
        ]

        self.all_records: List[Dict] = self.flatten(self._scrape_all_pages())

        # Remove Already Downloaded Hack Records
        self.records: List[Dict] = [
            record for record in self.all_records 
            if record['page_url'] not in self.already_scraped
        ]

    def bypass_ddos(self):
        self.session.post('https://www.smwcentral.net/', headers=self.headers, data={"unlock_me": "30"})

    def get_page_content(self, page: str) -> str:
        print(f"Bypassing DDoS:")
        self.bypass_ddos()
        print(f"Requesting page: {page}")
        res = self.session.get(page)
        res.raise_for_status()
        return str(res.content)


    def get_hack_pages_count(self, content: str) -> int:
        soup: BeautifulSoup = BeautifulSoup(content, "html.parser")
        last_page: Tag = soup.select_one('ul.page-list li:last-child')
        try:
            return int(last_page.string)
        except (ValueError, AttributeError):
            error_ref = last_page.string if last_page is not None else ""
            print(f"ERROOR failed to get pages. {error_ref}")
            sys.exit()


    def get_hack_pages_urls(self, base_url: str) -> List[str]:
        urls = []
        for page_number in range(1, self.hack_pages_count+1):
            urls.append(base_url + f"&n={page_number}")
        return urls
    

    def _scrape_all_pages(self) -> List[List[Dict]]:
        total_hacks_on_all_pages = []

        if DEBUG_SCRAPER["ONE_PAGE_ONLY"]:
            total_hacks_on_all_pages.append(self.scrape_hacks_list_page(self.hack_pages_urls[0]))
        else:
            for url in self.hack_pages_urls:
                total_hacks_on_all_pages.append(self.scrape_hacks_list_page(url))

        return total_hacks_on_all_pages


    def scrape_hacks_list_page(self, url: str) -> List[dict]:
        total_hacks_on_page: List[dict] = []
        content: str = self.get_page_content(url)
        page_soup: BeautifulSoup = BeautifulSoup(content, "html.parser")
        page_row_tags: List[Tag] = page_soup.select('table.list tbody tr')

        if DEBUG_SCRAPER["ONE_HACK_ONLY"]:
            self.scrape_row_from_hacks_list(page_row_tags[0])
        else:
            for row in page_row_tags:
                total_hacks_on_page.append(self.scrape_row_from_hacks_list(row))

        return total_hacks_on_page


    def scrape_row_from_hacks_list(self, row: Tag) -> dict:
        try:
            hack_title: str = self.scrape_title_from_row(row)
            hack_date: datetime = self.scrape_upload_time_from_row(row)
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
                'value': row.find_all('td')[7].string.split('\\xc2\\xa0')[0],
                'units': row.find_all('td')[7].string.split('\\xc2\\xa0')[1]
            }
            hack_download_url: str = row.find_all('td')[8].select_one('a')['href']
            hack_total_downloads: str = row.find_all('td')[8].select_one('span.secondary-info').string.split()[0].replace(',', '')
        except IndexError as e:
            print("Problem scraping size due to separator characters:")
            print(row.find_all('td')[7].string.split('\xc2\xa0')[0])
            sys.exit(1)

        record = {
            "title": hack_title,
            "created_on": hack_date,
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
        
        return record


    @staticmethod
    def scrape_url_from_row(row: Tag) -> str:
        base = "https://www.smwcentral.net"
        return base + row.select_one('td.text a')['href']


    @staticmethod
    def scrape_title_from_row(row: Tag) -> str:
        return row.select_one('td.text a').string


    @staticmethod
    def scrape_upload_time_from_row(row: Tag) -> datetime:
        t = row.select_one('time')['datetime']
        return datetime.strptime(t.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

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
  