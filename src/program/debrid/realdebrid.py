"""Realdebrid module"""
from program.media import MediaItem, MediaItemContainer, MediaItemState
from utils.logger import logger
from utils.request import get, post
from settings.manager import settings_manager

WANTED_FORMATS = ["mkv", "mp4"]


class Debrid:
    """Real-debrid.com debrider"""

    def __init__(self):
        self.settings = "debrid_realdebrid"
        self.class_settings = settings_manager.get(self.settings)
        self.auth_headers = {
            "Authorization": f'Bearer {self.class_settings["api_key"]}'
        }

    def download(self, media_items: MediaItemContainer):
        """Download given media items from real-debrid.com"""
        added_files = 0
        for item in media_items:
            if item.state == MediaItemState.SCRAPED:
                if self.check_availability(item):
                    request_id = self.add_magnet(item)
                    self.select_files(request_id, item)
                    item.change_state(MediaItemState.DOWNLOADING)
                    added_files += 1
                    logger.debug("Adding cached release for %s", item.title)
        if added_files > 0:
            logger.info("Downloaded %s cached releases", added_files)

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
                    for files in value:
                        files = next(
                            (
                                files
                                for file in files
                                if files[file]["filename"].split(".")[-1]
                                in WANTED_FORMATS
                            ),
                            None,
                        )
                        if files:
                            stream["files"] = files
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
