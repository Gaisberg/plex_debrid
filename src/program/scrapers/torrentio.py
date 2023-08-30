""" Torrentio scraper module """
from ratelimit import limits
from program.media import MediaItem, MediaItemContainer, MediaItemState
from utils.logger import logger
from utils.request import get
from utils.settings import settings_manager


class Scraper:
    """Scraper for torrentio"""

    def __init__(self):
        self.settings = "scraper_torrentio"
        self.class_settings = settings_manager.get(self.settings)

    def scrape(self, media_items: MediaItemContainer):
        """Scrape the torrentio site for the given media items
        and update the object with scraped streams"""
        scraped_amount = 0
        filters = f'sort=qualitysize%7Cqualityfilter={self.class_settings["filter"]}'
        for item in media_items:
            if (
                item.state == MediaItemState.CONTENT
                and item.scrape_tries <= 5
                and item.type == "movie"
            ):
                response = self.api_scrape(item, filters)
                if not response:
                    # logger.debug("Hit request cap, lets try again next cycle")
                    break
                streams = response["streams"]
                if len(streams) > 0:
                    item.streams = streams
                    item.change_state(MediaItemState.SCRAPED)
                    scraped_amount += 1
                    logger.debug("Found %s streams for %s", len(streams), item.title)
                else:
                    logger.debug("Could not find scraped streams for %s", item.title)
        if scraped_amount > 0:
            logger.info("Scraped %s streams", scraped_amount)

    @limits(calls=1, period=1, raise_on_limit=False)
    def api_scrape(self, item: MediaItem, filters: str):
        """Wrapper for torrentio scrape method"""
        response = get(
            f"https://torrentio.strem.fun/{filters}"
            + f"/stream/{item.type}/{item.imdb_id}.json"
        )
        item.scrape_tries += 1
        return response
