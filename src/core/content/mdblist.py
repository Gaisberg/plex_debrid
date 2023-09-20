"""Mdblist content module"""
from utils.settings import settings_manager
from utils.logger import logger
from utils.request import RateLimitExceeded, RateLimiter, get
from core.media import MediaItemContainer


class Mdblist:
    """Content class for mdblist"""

    def __init__(
        self,
    ):
        self.settings = settings_manager.get("mdblist")
        self.requests_per_2_minutes = self._calculate_request_time()
        self.rate_limiter = RateLimiter(self.requests_per_2_minutes, 120, True)

    def get_items(self):
        """Fetch imdb_ids of all items from mdblist lists"""
        items = set()
        try:
            with self.rate_limiter:
                logger.info("Getting items...")
                for list_id in self.settings["lists"]:
                    if list_id:
                        items.update(self._get_items_from_list(
                            list_id, self.settings["api_key"]
                        ))
        except RateLimitExceeded:
            pass
        return items

    def _get_items_from_list(self, list_id: str, api_key: str) -> MediaItemContainer:
        return {item.imdb_id for item in list_items(list_id, api_key)}

    def _calculate_request_time(self):
        limits = my_limits(self.settings["api_key"]).limits
        daily_requests = limits.api_requests
        requests_per_2_minutes = daily_requests / 24 / 60 * 2
        return requests_per_2_minutes


# API METHODS


def my_limits(api_key: str):
    """Wrapper for mdblist api method 'My limits'"""
    response = get(f"http://www.mdblist.com/api/user?apikey={api_key}")
    return response.data


def list_items(list_id: str, api_key: str):
    """Wrapper for mdblist api method 'List items'"""
    response = get(f"http://www.mdblist.com/api/lists/{list_id}/items?apikey={api_key}")
    return response.data
