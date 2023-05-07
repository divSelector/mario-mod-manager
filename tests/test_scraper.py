import pytest

from smwc.scraper import SMWCentralScraper

class TestSMWCentralScraper:

    def test_get_page_content_is_string(self, mock_scraper: SMWCentralScraper) -> None:
        assert isinstance(mock_scraper.hacks_page_content, str)

    def test_get_hack_pages_count_valid(self, mock_scraper: SMWCentralScraper) -> None:
        assert mock_scraper.get_hack_pages_count(
            mock_scraper.hacks_page_content
        ) == 42

    def test_get_hack_pages_count_invalid(self, mock_scraper: SMWCentralScraper) -> None:
        content = "<html><head></head><body></body></html>"
        with pytest.raises(SystemExit):
            mock_scraper.get_hack_pages_count(content)

    def test_get_hack_pages_count_not_numeric(self, mock_scraper: SMWCentralScraper) -> None:
        content = "<html><head></head><body><ul class='page-list'><li>1</li><li>2</li><li>three</li></ul></body></html>"
        with pytest.raises(SystemExit):
            mock_scraper.get_hack_pages_count(content)