"""Realdebrid module"""
from program.media import MediaItem
from utils.logger import logger
from utils.request import get, post
from settings.manager import settings_manager


class Debrid:
    """Real-debrid.com debrider"""

    def __init__(self):
        self.settings = "debrid_realdebrid"
        self.class_settings = settings_manager.get(self.settings)
        self.auth_headers = {
            "Authorization": f'Bearer {self.class_settings["api_key"]}'
        }

    def download(self, media_items: list[MediaItem]):
        """Download given media items from real-debrid.com"""
        for item in media_items:
            if item.state == MediaItem.STATE_SCRAPED:
                if self.check_availability(item):
                    request_id = self.add_magnet(item)
                    self.select_files(request_id, item)
                    item.state = MediaItem.STATE_IN_DOWNLOAD
                    logger.debug("Adding cached release for %s", item.title)

    def check_availability(self, media_item: MediaItem) -> bool:
        """Check if media item is cached in real-debrid.com"""
        for stream in media_item.streams:
            infohash = stream["infoHash"]
            response = get(
                f"https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{infohash}/",
                additional_headers=self.auth_headers,
            )
            stream["files"] = {}
            if len(response[infohash]) > 0:
                for _, value in response[infohash].items():
                    for file_id in value:
                        stream["files"] = file_id
                        media_item.streams = stream

                        return True
            return False

    def add_magnet(self, item: MediaItem) -> str:
        """Add magnet link to real-debrid.com"""
        response = post(
            "https://api.real-debrid.com/rest/1.0/torrents/addMagnet",
            {"magnet": "magnet:?xt=urn:btih:" + item.streams["infoHash"] + "&dn=&tr="},
            additional_headers=self.auth_headers,
        )
        return response["id"]

    def select_files(self, request_id, item) -> None:
        """Select files from real-debrid.com"""
        post(
            f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{request_id}",
            {"files": ",".join(item.streams["files"].keys())},
            additional_headers=self.auth_headers,
        )

    # TODO Implement more realdebrid api methods here
