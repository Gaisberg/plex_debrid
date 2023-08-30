"""MediaItem module"""

from enum import Enum


class MediaItemState(Enum):
    """MediaItem states"""

    STATE_UNKNOWN = -1
    READY = 0
    CONTENT = 1
    SCRAPED = 2
    DOWNLOADING = 3
    METADATA_REQUIRED = 4


class MediaItem:
    """MediaItem class"""

    def __init__(self, item, state=MediaItemState.STATE_UNKNOWN):
        self.title = item["title"]
        self.type = item["type"]
        self.state = state
        self.streams = None
        self.scrape_tries = 0
        self.download_tries = 0
        if "year" in item:
            self.release_year = item["year"]
        if "imdb_id" in item:
            self.imdb_id = item["imdb_id"]
        if "library_section" in item:
            self.library_section = item["library_section"]
        if "key" in item:
            self.key = item["key"]
        if "guid" in item:
            self.guid = item["guid"]

    def change_state(self, state) -> bool:
        """Change object state"""
        if self.state != state:
            self.state = state
            return True
        return False

    def __eq__(self, other):
        return self.title == other.title and self.type == other.type

    def __iter__(self):
        for attr, _ in vars(self).items():
            yield attr


class MediaItemContainer:
    """MediaItemContainer class"""

    def __init__(self, items: list[MediaItem] = None):
        self.items = []
        if items:
            self.items = items

    def __iter__(self):
        for item in self.items:
            yield item

    def __iadd__(self, other):
        for item in other:
            if item not in self.items:
                self.items.append(item)
        return self

    def update(self, other: MediaItem):
        for item in self.items:
            if item == other:
                item = other

    def count(self, state) -> int:
        """Count items with given state in container"""
        return len([item for item in self.items if item.state == state])

    def get_sections_needing_update(self, sections):
        """Get sections that need to be updated"""
        sections_needed = []
        for section in sections:
            if not sections[section]["refreshing"]:
                for item in self.items:
                    if (
                        item.type == sections[section]["type"]
                        and section not in sections_needed
                        and item.state == MediaItemState.DOWNLOADING
                    ):
                        sections_needed.append(section)
        return sections_needed

    def get_items_needing_metadata(self):
        """Get items that need to be updated"""
        items_needing_metadata = []
        for item in self.items:
            if item.state == MediaItemState.METADATA_REQUIRED:
                items_needing_metadata.append(item)
        return items_needing_metadata

    def append(self, item) -> bool:
        """Append item to container"""
        if item not in self.items:
            self.items.append(item)
            return True
        return False

    def __len__(self):
        """Get length of container"""
        return len(self.items)
