"""Trakt updater module"""
from utils.logger import logger
from utils.request import get
from program.media import MediaItemState


CLIENT_ID = "0183a05ad97098d87287fe46da4ae286f434f32e8e951caad4cc147c947d79a3"


class Updater:
    """Trakt updater class"""

    def update_items(self, media_items):
        """Update media items to state where they can start downloading"""
        for media_item in media_items:
            searched_item = None
            for key, value in media_item.ids.items():
                if value is not None:
                    searched_item = search_id_lookup(key, value, media_item.type)
                    if searched_item and searched_item["ids"][key] == value:
                        break
            if not searched_item:
                logger.debug("Could not update with trakt: %s", media_item.ids)
                media_item.change_state(MediaItemState.ERROR)
            if searched_item:
                searched_item["type"] = media_item.type
                media_item.set("ids.imdb", searched_item["ids"]["imdb"])
                media_item.set("title", searched_item["title"])
                media_item.set("year", searched_item["year"])
                logger.debug("Updated %s", media_item.title)


# API METHODS


def search_id_lookup(id_type: str, item_id: str, item_type: str):
    """Wrapper for trakt.tv API search method"""
    response = get(
        f"https://api.trakt.tv/search/{id_type}/{item_id}?extended=full,type={item_type}",
        additional_headers={"trakt-api-version": "2", "trakt-api-key": CLIENT_ID},
    )
    if response.is_ok:
        if response.data:
            return response.data[0].get(item_type, None)
    return None
