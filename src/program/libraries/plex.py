"""Plex library module"""
import datetime
from program.media import MediaItem
from utils.logger import logger
from utils.request import get
from settings.manager import settings_manager as settings


class Library:
    """Plex library class"""

    def __init__(self):
        self.settings = "library_plex"
        self.class_settings = settings.get(self.settings)

    def _get_sections(self):
        response = get(
            self.class_settings["address"]
            + "/library/sections/?X-Plex-Token="
            + self.class_settings["token"]
        )
        sections = {}
        for section in response["MediaContainer"]["Directory"]:
            sections[section["key"]] = {
                "title": section["title"],
                "type": section["type"],
            }
        return sections

    def update_items(self, media_items):
        """Update media_items attribute with items in plex library"""
        sections = self._get_sections()
        added_items = 0
        for item in sections.items():
            response = get(
                self.class_settings["address"]
                + "/library/sections/"
                + item[0]
                + "/all?X-Plex-Token="
                + self.class_settings["token"]
            )
            for data in response["MediaContainer"]["Metadata"]:
                if "originalTitle" in data:
                    data["title"] = data["originalTitle"]
                data["release_year"] = datetime.datetime.strptime(
                    data["originallyAvailableAt"], "%Y-%M-%d"
                ).year
                _item = MediaItem(data, MediaItem.STATE_IN_LIBRARY)
                existing_item = next(
                    (
                        item
                        for item in media_items
                        if item == _item and item.state == MediaItem.STATE_IN_DOWNLOAD
                    ),
                    None,
                )
                if existing_item:
                    existing_item.state = MediaItem.STATE_IN_LIBRARY
                    existing_item.streams = None
                    added_items += 1
                if _item not in media_items:
                    added_items += 1
                    media_items.append(_item)
        logger.debug("Found %s existing items", added_items)

    # TODO Implement more plex api methods here
