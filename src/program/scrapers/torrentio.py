""" Torrentio scraper module """
import datetime
import time
from utils.logger import logger
from utils.request import get
from utils.settings import settings_manager
from program.media import MediaItem, MediaItemContainer, MediaItemState


class Scraper:
    """Scraper for torrentio"""

    def __init__(self):
        self.settings = "scraper_torrentio"
        self.class_settings = settings_manager.get(self.settings)
        self.last_scrape = 0

    def scrape(self, media_items: MediaItemContainer):
        """Scrape the torrentio site for the given media items
        and update the object with scraped streams"""
        logger.info("Scraping...")
        scraped_amount = 0
        filters = f'sort=qualitysize%7Cqualityfilter={self.class_settings["filter"]}'

        for item in media_items:
            if (
                (
                    item.scraped_at == 0
                    or datetime.datetime.now().timestamp() - item.scraped_at >= 3600
                )
                and item.type == "movie"
                and item.ids.get("imdb")
                and item.state == MediaItemState.CONTENT
            ):
                delta = datetime.datetime.now().timestamp() - self.last_scrape
                if self.last_scrape != 0 and delta < 1:
                    time.sleep(1 - delta)
                response = self.api_scrape(item, filters)
                if not response.is_ok:
                    break
                if response.data:
                    streams = response.data["streams"]
                    if len(streams) > 0:
                        item.set("streams", streams)
                        item.change_state(MediaItemState.SCRAPED)
                        scraped_amount += 1
                        logger.debug(
                            "Found %s streams for %s", len(streams), item.title
                        )
                    else:
                        logger.debug(
                            "Could not find scraped streams for %s", item.title
                        )
        if scraped_amount > 0:
            logger.info("Scraped %s streams", scraped_amount)
        logger.info("Done!")

    def api_scrape(self, item: MediaItem, filters: str):
        """Wrapper for torrentio scrape method"""
        response = get(
            f"https://torrentio.strem.fun/{filters}"
            + f"/stream/{item.type}/{item.ids.get('imdb')}.json"
        )
        timestamp = datetime.datetime.now().timestamp()
        self.last_scrape = timestamp
        item.set("scraped_at", timestamp)
        return response
