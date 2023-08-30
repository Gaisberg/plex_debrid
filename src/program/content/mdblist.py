"""Mdblist content module"""
from program.media import MediaItem, MediaItemContainer, MediaItemState
from utils.settings import settings_manager
from utils.logger import logger
from utils.request import get


class Content:
    """Content class for mdblist"""

    def __init__(
        self,
    ):
        self.settings = "content_mdblist"
        self.class_settings = settings_manager.get(self.settings)

    def update_items(self, media_items: MediaItemContainer):
        """Fetch media from mdblist and add them to media_items attribute
        if they are not already there"""
        fetched_items = MediaItemContainer()
        for list_id in self.class_settings["lists"]:
            fetched_items += self.get_items_from_list(
                list_id, self.class_settings["api_key"]
            )
        added_items = 0
        for fetched_item in fetched_items:
            if fetched_item not in media_items:
                media_items.append(fetched_item)
                added_items += 1
                logger.debug("Added '%s'", fetched_item.title)
        if added_items > 0:
            logger.info("Found %s new items", added_items)

    # Mdblist api method wrappers
    def get_items_from_list(self, list_id: str, api_key: str) -> MediaItemContainer:
        """Wrapper for mdblist api method get_items_from_list"""
        fetched_items = get(
            f"http://www.mdblist.com/api/lists/{list_id}" + f"/items?apikey={api_key}"
        )
        media_item_container = MediaItemContainer()
        for fetched_item in fetched_items:
            fetched_item["type"] = fetched_item["mediatype"]
            fetched_item["year"] = fetched_item["release_year"]
            media_item_container.append(MediaItem(fetched_item, MediaItemState.CONTENT))
        return media_item_container
