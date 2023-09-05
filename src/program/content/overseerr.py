"""Mdblist content module"""
from utils.settings import settings_manager
from utils.logger import logger
from utils.request import get
from program.media import MediaItem, MediaItemContainer, MediaItemState
from program.updaters.trakt import Updater as Trakt


class Content:
    """Content class for mdblist"""

    def __init__(
        self,
    ):
        self.settings = "content_overseerr"
        self.class_settings = settings_manager.get(self.settings)
        self.mdb_api_key = settings_manager.get("content_mdblist")["api_key"]
        self.updater = Trakt()
        self.items = MediaItemContainer()

    def update_items(self, media_items: MediaItemContainer):
        """Fetch media from overseerr and add them to media_items attribute
        if they are not already there"""
        logger.info("Getting items...")
        self.items.load("data/overseerr_data.pkl")
        fetched_items = self._get_items_from_overseerr(1000)
        added_items = MediaItemContainer(self.items.extend(fetched_items))
        self.updater.update_items(added_items)
        added_items = media_items.extend(added_items)
        if len(added_items) > 0:
            for item in added_items:
                logger.debug("Added %s", item.title)
            logger.info("Found %s new items", len(added_items))
        self.items.extend(added_items)
        self.items.save("data/overseerr_data.pkl")
        logger.info("Done!")

    def _get_items_from_overseerr(self, amount: int):
        """Fetch media from overseerr"""
        response = get_requests(
            self.class_settings["url"], self.class_settings["api_key"], amount
        )
        fetched_items = MediaItemContainer()
        for fetched_item in response["results"]:
            if fetched_item["type"] == "tv":
                fetched_item["type"] = "show"
            fetched_item["imdb"] = fetched_item["media"]["imdbId"]
            fetched_item["tmdb"] = fetched_item["media"]["tmdbId"]
            fetched_item["tvdb"] = fetched_item["media"]["tvdbId"]
            new_item = MediaItem(fetched_item, MediaItemState.CONTENT)
            fetched_items.append(new_item)
        return fetched_items


# API METHODS
def get_requests(overseerr_url: str, api_key: str, amount: int) -> dict:
    """Wrapper for overseerr api method get_requests"""
    response = get(
        overseerr_url + f"/api/v1/request?take={amount}",
        additional_headers={"X-Api-Key": api_key},
    )
    return response.data


def get_movie_details(overseerr_url: str, api_key: str, movie_id: str) -> dict:
    """Wrapper for overseerr api method get_movie_details"""
    response = get(
        overseerr_url + f"/api/v1/movie/{movie_id}",
        additional_headers={"X-Api-Key": api_key},
    )
    return response.data


def get_tv_details(overseerr_url: str, api_key: str, tv_id: str) -> dict:
    """Wrapper for overseerr api method get_tv_details"""
    response = get(
        overseerr_url + f"/api/v1/tv/{tv_id}", additional_headers={"X-Api-Key": api_key}
    )
    return response.data
