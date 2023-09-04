"""Mdblist content module"""
import datetime
from utils.settings import settings_manager as s
from utils.logger import logger
from utils.request import get
from program.media import MediaItem, MediaItemContainer, MediaItemState


class Content:
    """Content class for mdblist"""

    def __init__(
        self,
    ):
        self.settings = "content_mdblist"
        self.last_update = 0

    def update_items(self, media_items: MediaItemContainer):
        """Fetch media from mdblist and add them to media_items attribute
        if they are not already there"""
        logger.info("Getting items...")
        settings = s.get(self.settings)

        if (
            self.last_update == 0
            or datetime.datetime.now().timestamp() - self.last_update
            > settings["update_interval"]
        ):
            fetched_items = MediaItemContainer()
            for list_id in settings["lists"]:
                fetched_items += self._get_items_from_list(list_id, settings["api_key"])
            added_items = 0
            for fetched_item in fetched_items:
                if fetched_item not in media_items:
                    media_items.append(fetched_item)
                    added_items += 1
                    logger.debug("Added '%s'", fetched_item.title)
            if added_items > 0:
                logger.info("Found %s new items", added_items)

            self.last_update = datetime.datetime.now().timestamp()
        logger.info("Done!")

    def _get_items_from_list(self, list_id: str, api_key: str) -> MediaItemContainer:
        fetched_items = list_items(list_id, api_key)
        media_item_container = MediaItemContainer()
        for fetched_item in fetched_items:
            new_item = {
                "title": fetched_item.get("title"),
                "year": fetched_item.get("release_year"),
                "imdb": fetched_item.get("imdb_id"),
                "type": fetched_item.get("mediatype"),
            }
            media_item_container.append(MediaItem(new_item, MediaItemState.CONTENT))
        logger.debug("returned %s", media_item_container)
        return media_item_container


# API METHODS


def list_items(list_id: str, api_key: str):
    """Wrapper for mdblist api method 'List items'"""
    response = get(f"http://www.mdblist.com/api/lists/{list_id}/items?apikey={api_key}")
    return response.data
