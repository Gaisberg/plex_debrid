"""MediaItem module"""

import datetime
from enum import Enum
import threading


class MediaItemState(Enum):
    """MediaItem states"""

    ERROR = -1
    UNKNOWN = 1
    LIBRARY = 2
    LIBRARY_METADATA = 3
    CONTENT = 4
    SCRAPED = 5
    DOWNLOADING = 6


class MediaItem:
    """MediaItem class"""

    def __init__(self, item, state=MediaItemState.UNKNOWN):
        self._lock = threading.Lock()
        self.title = item.get("title", None)
        self.type = item.get("type", None)
        self.file_name = item.get("file_name", None)
        self.streams = None
        self.scrape_tries = 0
        self.download_tries = 0
        self.ids = item.get(
            "ids",
            {
                "tmdb": item.get("tmdb", None),
                "tvdb": item.get("tvdb", None),
                "imdb": item.get("imdb", None),
            },
        )
        self.year = item.get("year", None)
        self.library_section = item.get("library_section", None)
        self.key = item.get("key", None)
        self.guid = item.get("guid", None)
        self.state = state
        self.scraped_at = 0

    def __eq__(self, other):
        with self._lock:
            return (
                any(
                    key in other.ids.keys()
                    and self.ids[key] is not None
                    and self.ids[key] == other.ids[key]
                    for key in self.ids.keys()
                )
                or self.guid is not None
                and self.guid == other.get("guid")
                or self.title is not None
                and self.title == other.get("title")
                and self.year is not None
                and self.year == other.get("year")
            )

    def __iter__(self):
        with self._lock:
            for attr, _ in vars(self).items():
                yield attr

    def change_state(self, state) -> bool:
        """Change object state"""
        with self._lock:
            if self.state != state:
                self.state = state
                return True
            return False

    def get(self, key, default=None):
        """Get item attribute"""
        with self._lock:
            return getattr(self, key) or default

    def set(self, key, value):
        """Set item attribute"""
        with self._lock:
            setattr(self, key, value)


class MediaItemContainer:
    """MediaItemContainer class"""

    def __init__(self, items: list[MediaItem] = None):
        self.items = []
        if items:
            self.items = items
        self.updated_at = None

    def __iter__(self):
        for item in self.items:
            yield item

    def __iadd__(self, other):
        for item in other:
            if item not in self.items:
                self.items.append(item)
                self._set_updated_at()
        return self

    def append(self, item) -> bool:
        """Append item to container"""
        if item not in self.items:
            self.items.append(item)
            self._set_updated_at()
            return True
        return False

    def _set_updated_at(self):
        self.updated_at = {
            "length": len(self.items),
            "time": datetime.datetime.now().timestamp(),
        }

    def remove(self, item):
        """Remove item from container"""
        if item in self.items:
            self.items.remove(item)
            self._set_updated_at()

    def count(self, state) -> int:
        """Count items with given state in container"""
        return len(self.get_items_with_state(state))

    def change_item_state(self, item, state) -> bool:
        """Change item state"""
        if item in self.items:
            item.change_state(state)
            return True
        return False

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

    def get_items_with_state(self, state):
        """Get items that need to be updated"""
        return MediaItemContainer([item for item in self.items if item.state == state])

    def __len__(self):
        """Get length of container"""
        return len(self.items)

    def has_changed(self):
        """Check if container has changed"""
        if self.updated_at is None:
            return False
        return len(self.items) != self.updated_at["length"]

    def is_empty(self):
        """Check if container is empty"""
        return len(self.items) == 0
