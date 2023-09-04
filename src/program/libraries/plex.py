"""Plex library module"""
from utils.logger import logger
from utils.request import get, put
from utils.settings import settings_manager as settings
from program.media import MediaItem, MediaItemContainer, MediaItemState


class Library:
    """Plex library class"""

    def __init__(self):
        self.settings = "library_plex"
        self.class_settings = settings.get(self.settings)
        self.class_settings["sections"] = self._get_libraries()

    def get_new_items(self, media_items: MediaItemContainer):
        """Update media_items attribute with items in plex library"""
        logger.info("Getting items...")
        added_items = []
        sections = self.class_settings["sections"].items()
        for section in sections:
            fetched_items = self._get_all_section_items(section)
            added_items = added_items + media_items.extend(fetched_items)
        if len(added_items) > 0:
            logger.info("Found %s new items", len(added_items))
        logger.info("Done!")

    def update_sections(self, media_items: MediaItemContainer):
        """Update plex library section"""
        sections = media_items.get_sections_needing_update(self._get_libraries())
        if media_items.count(MediaItemState.DOWNLOADING) > 0:
            for section in sections:
                self._update_library_section(section)
                logger.info("%s sections updated", len(sections))

    def update_metadata_for_items(self, media_items: MediaItemContainer):
        """Update plex library item metadata"""
        for item in media_items:
            if item.state == MediaItemState.LIBRARY_METADATA:
                self._update_item_metadata(item)

    def match_items(self, media_items: MediaItemContainer):
        """Matches items in given mediacontainer that are not in library
        to items that are in library"""
        match_time = len(media_items) * 0.033
        logger.info("Matching items... will take around %s seconds", match_time)

        # Categorize items into dictionaries for faster lookup
        items_by_guid = {}
        items_by_filename = {}
        for item in media_items:
            if item.state in [MediaItemState.LIBRARY, MediaItemState.LIBRARY_METADATA]:
                if item.guid:
                    items_by_guid[(item.type, item.guid)] = item
                if item.file_name:
                    items_by_filename[(item.type, item.file_name)] = item

        movie_key = next(
            (item.key for item in media_items if item.type == "movie" and item.guid),
            None,
        )
        show_key = next(
            (item.key for item in media_items if item.type == "show" and item.guid),
            None,
        )

        remove_these = []
        for item in media_items:
            if item.state is not MediaItemState.LIBRARY:
                if item.type == "movie":
                    agent = "tv.plex.agents.movie"
                    any_key = movie_key
                else:
                    agent = "tv.plex.agents.series"
                    any_key = show_key

                if any_key:
                    guid = self._match(any_key, item, agent)

                    library_item = items_by_guid.get(
                        (item.type, guid)
                    ) or items_by_filename.get((item.type, item.file_name))
                    if library_item:
                        state = MediaItemState.LIBRARY
                        if library_item.guid != guid:
                            state = MediaItemState.LIBRARY_METADATA

                        item.set("guid", guid)
                        item.set("key", library_item.key)
                        item.set("file_name", library_item.file_name)
                        if item.title is None:
                            item.set("title", library_item.title)
                        if item.year is None:
                            item.set("year", library_item.year)
                        item.change_state(state)
                        remove_these.append(library_item)

        for item in remove_these:
            media_items.remove(item)
        logger.info("Done!")

    def _get_all_section_items(
        self, section: int, request_filter=None
    ) -> MediaItemContainer:
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
        if response.is_ok:
            fetched_container = response.data["MediaContainer"]
            if "Metadata" in fetched_container:
                for fetched_item in fetched_container["Metadata"]:
                    state = MediaItemState.LIBRARY_METADATA
                    if "summary" in fetched_item and len(fetched_item["summary"]) > 0:
                        state = MediaItemState.LIBRARY
                    if "originalTitle" in fetched_item:
                        fetched_item["title"] = fetched_item["originalTitle"]
                    file_name = next(
                        part for part in fetched_item["Media"][0]["Part"] if part
                    )
                    file_name = file_name["file"].split("\\")[-1]
                    fetched_item["file_name"] = file_name
                    media_item_container.append(MediaItem(fetched_item, state))
        return media_item_container

    def _get_libraries(self):
        """Wrapper for plex api get libraries method"""
        response = get(
            self.class_settings["address"]
            + "/library/sections/?X-Plex-Token="
            + self.class_settings["token"]
        )

        sections = {}
        if response.is_ok:
            for section in response.data["MediaContainer"]["Directory"]:
                sections[section["key"]] = {
                    "title": section["title"],
                    "type": section["type"],
                    "refreshing": section["refreshing"],
                }
        return sections

    def _update_library_section(self, section):
        """Update plex library section"""
        response = get(
            self.class_settings["address"]
            + "/library/sections/"
            + section
            + "/refresh"
            + "?X-Plex-Token="
            + self.class_settings["token"]
        )
        if response.is_ok:
            logger.debug(
                "Section %s updated",
                section,
            )

    def _update_item_metadata(self, item):
        """Update plex library item metadata"""
        url = (
            self.class_settings["address"] + item.key + "/match?" + f"guid={item.guid}"
        )
        if "title" in item:
            url += f"&name={item.title}"
        if "year" in item:
            url += f"&year={item.year}"
        url += "&X-Plex-Token=" + self.class_settings["token"]
        response = put(url)
        if response.is_ok:
            logger.debug("Item '%s' metadata updated", item.title)

    def _match(self, any_key, item, agent):
        """Get matches for plex item"""
        for key, value in item.ids.items():
            if value is not None and key in ["imdb", "tmdb", "tvdb"]:
                match = get(
                    self.class_settings["address"]
                    + any_key
                    + f"/matches?manual=1&title={key}-{value}"
                    + f"&agent={agent}&language=en-US&X-Plex-Token="
                    + self.class_settings["token"]
                )
                if match.is_ok:
                    if "MediaContainer" in match.data:
                        if "SearchResult" in match.data["MediaContainer"]:
                            if len(match.data["MediaContainer"]["SearchResult"]) > 0:
                                return match.data["MediaContainer"]["SearchResult"][0][
                                    "guid"
                                ]
        return None
