''' Torrentio scraper module '''
from program.media import MediaItem
from utils.logger import logger
from utils.request import get
from settings.manager import settings_manager


class Scraper:
    ''' Scraper for torrentio '''
    def __init__(self):
        self.settings = "scraper_torrentio"
        self.class_settings = settings_manager.get(self.settings)

    def scrape(self, media_items):
        """Scrape the torrentio site for the given media items
        and update the object with scraped streams"""
        scraped_amount = 0
        if scraped_amount >= 100:
            return
        for item in media_items:
            if item.state == MediaItem.STATE_IN_CONTENT_SERVICE:
                item_type = item.type
                if item.type == "show":
                    item_type = "series"
                    continue
                filters = (
                    f'sort=qualitysize%7Cqualityfilter={self.class_settings["filter"]}'
                )
                url = str(
                    f"https://torrentio.strem.fun/{filters}"
                    + f"/stream/{item_type}/{item.imdb_id}.json"
                )
                scraped_amount += 1
                response = get(url)
                if not response:
                    logger.debug("Hit request cap, lets try again next cycle")
                    break
                streams_amount = len(response["streams"])
                if streams_amount > 0:
                    item.streams = response["streams"]
                    item.state = MediaItem.STATE_SCRAPED
                    logger.debug("Found %s streams for %s", streams_amount, item.title)
                else:
                    logger.debug("Could not find scraped streams for %s", item.title)
