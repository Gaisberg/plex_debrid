"""Plex library module"""
from program.media import MediaItem, MediaItemContainer, MediaItemState
from utils.logger import logger
from utils.request import get, put
from settings.manager import settings_manager as settings


class Library:
    """Plex library class"""

    def __init__(self):
        self.settings = "library_plex"
        self.class_settings = settings.get(self.settings)
        self.class_settings["sections"] = self.get_libraries()

    def update_items(self, media_items: MediaItemContainer):
        """Update media_items attribute with items in plex library"""
        added_items = 0
        sections = self.class_settings["sections"].items()
        for section in sections:
            fetched_items = self.get_all_section_items(section)
            for fetched_item in fetched_items:
                if fetched_item not in media_items:
                    media_items.append(fetched_item)
                    added_items += 1

        if added_items > 0:
            logger.info("Found %s new items", added_items)

    def update_sections(self, media_items: MediaItemContainer):
        """Update plex library section"""
        if media_items.count(MediaItemState.DOWNLOADING) > 0:
            sections = media_items.get_sections_needing_update(self.get_libraries())
            for section in sections:
                self.update_library_section(section)
                logger.info("%s sections updated", len(sections))

    def update_metadata_for_items(self, media_items: MediaItemContainer):
        """Update plex library item metadata"""
        if media_items.count(MediaItemState.METADATA_REQUIRED) > 0:
            items_needing_metadata = media_items.get_items_needing_metadata()
            for item in items_needing_metadata:
                self.update_item_metadata(item)
                logger.info("%s items metadata updated", len(items_needing_metadata))

    # Plex api method wrappers
    def get_all_section_items(
        self, section: int, request_filter=None
    ) -> MediaItemContainer:
        """Wrapper for plex api Get All Movies and Get All TV Shows methods"""
        url = str(
            self.class_settings["address"]
            + "/library/sections/"
            + section[0]
            + "/all?X-Plex-Token="
            + self.class_settings["token"]
        )
        if request_filter:
            url += f"&{request_filter}"
        response = get(url)
        media_item_container = MediaItemContainer()
        fetched_container = response["MediaContainer"]
        if "Metadata" in fetched_container:
            for fetched_item in fetched_container["Metadata"]:
                state = MediaItemState.METADATA_REQUIRED
                if "summary" in fetched_item and len(fetched_item["summary"]) > 0:
                    state = MediaItemState.READY
                    if "originalTitle" in fetched_item:
                        fetched_item["title"] = fetched_item["originalTitle"]
                media_item_container.append(MediaItem(fetched_item, state))
        # logger.debug("Section %s items fetched", len(media_item_container))
        return media_item_container

    def get_libraries(self):
        """Wrapper for plex api get libraries method"""
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
                "refreshing": section["refreshing"],
            }
        return sections

    def update_library_section(self, section):
        """Update plex library section"""
        response = get(
            self.class_settings["address"]
            + "/library/sections/"
            + section
            + "/refresh"
            + "?X-Plex-Token="
            + self.class_settings["token"]
        )
        if response:
            logger.debug(
                "Section %s updated",
                section,
            )

    def update_item_metadata(self, item):
        """Update plex library item metadata"""
        url = (
            self.class_settings["address"] + item.key + "/match?" + f"guid={item.guid}"
        )
        if "title" in item:
            url += f"&name={item.title}"
        if "release_year" in item:
            url += f"&year={item.release_year}"
        url += "&X-Plex-Token=" + self.class_settings["token"]
        response = put(url)
        if response:
            logger.debug("Item '%s' metadata updated", item.title)
