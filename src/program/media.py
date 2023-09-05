"""MediaItem module"""

import datetime
from enum import Enum
import threading
import dill


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
                self.file_name is not None
                and self.file_name == other.file_name
                or any(
                    key in other.ids.keys()
                    and self.ids[key] is not None
                    and self.ids[key] == other.ids[key]
                    for key in self.ids.keys()
                )
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
            _set_nested_attr(self, key, value)


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

    def __len__(self):
        """Get length of container"""
        return len(self.items)

    def append(self, item) -> bool:
        """Append item to container"""
        self.items.append(item)
        self._set_updated_at()

    def get(self, item) -> MediaItem:
        """Get item matching given item from container"""
        for my_item in self.items:
            if my_item == item:
                return my_item
        return None

    def extend(self, items) -> "MediaItemContainer":
        """Extend container with items"""
        added_items = MediaItemContainer()
        for media_item in items:
            if media_item not in self.items:
                self.items.append(media_item)
                added_items.append(media_item)
        return added_items

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

    def save(self, filename):
        """Save container to file"""
        with open(filename, "wb") as file:
            dill.dump(self.items, file)

    def load(self, filename):
        """Load container from file"""
        try:
            with open(filename, "rb") as file:
                self.items = dill.load(file)
        except FileNotFoundError:
            self.items = []


def _set_nested_attr(obj, key, value):
    if "." in key:
        parts = key.split(".", 1)
        current_key, rest_of_keys = parts[0], parts[1]

        if not hasattr(obj, current_key):
            raise AttributeError(f"Object does not have the attribute '{current_key}'.")

        current_obj = getattr(obj, current_key)
        _set_nested_attr(current_obj, rest_of_keys, value)
    else:
        if isinstance(obj, dict):
            if key in obj:
                obj[key] = value
        else:
            setattr(obj, key, value)
