from database import SMWCentralDatabase
from scraper import SMWCentralScraper

def scrape():
    scraper = SMWCentralScraper()
    db.open_database(
    db.write_records, 
    action_param=scraper.records
)

db = SMWCentralDatabase('smwcentral.db')
