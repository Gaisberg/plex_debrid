"""Mdblist content module"""
from program.media import MediaItem
from settings.manager import settings_manager
from utils.logger import logger
from utils.request import get


class Content:
    """Content class for mdblist"""

    def __init__(
        self,
    ):
        self.settings = "content_mdblist"
        self.class_settings = settings_manager.get(self.settings)

    def update_items(self, media_items):
        """Fetch media from mdblist and add them to media_items attribute
        if they are not already there"""
        fetched_items = []
        for list_id, _ in self.class_settings["lists"].items():
            url = str(
                f"http://www.mdblist.com/api/lists/{list_id}"
                + f'/items?apikey={self.class_settings["api_key"]}'
            )
            fetched_items += get(url)

        added_items = 0
        for item in fetched_items:
            _item = {}
            _item["imdb_id"] = item["imdb_id"]
            _item["type"] = item["mediatype"]
            _item["release_year"] = item["release_year"]
            _item["title"] = item["title"]
            final_item = MediaItem(_item, MediaItem.STATE_IN_CONTENT_SERVICE)
            if final_item not in media_items:
                added_items += 1
                media_items.append(final_item)
        logger.debug("Added %s items to be scraped and downloaded", added_items)

    # TODO Implement more mdblist api methods here
