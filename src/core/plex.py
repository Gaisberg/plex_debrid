"""Plex library module"""
import os
import copy
from plexapi.server import PlexServer
from requests.exceptions import ReadTimeout
from utils.logger import logger
from utils.settings import settings_manager as settings
from core.media import (
    Episode,
    MediaItemContainer,
    MediaItemState,
    Movie,
    Season,
    Show,
)


class Library:
    """Plex library class"""

    def __init__(self):
        plex_settings = settings.get("plex")
        self.plex = PlexServer(
            plex_settings["address"], plex_settings["token"], timeout=5
        )

    def update_items(self, media_items: MediaItemContainer):
        """Update media_items attribute with items in plex library"""
        logger.info("Getting items...")
        added_items = 0
        items = MediaItemContainer()
        sections = self.plex.library.sections()
        for section in sections:
            if not section.refreshing:
                for item in section.all():
                    items += self._create_item(item)
        media_items.extend(self.match_items(items, media_items))
        added_items += len(media_items.extend(items))
        if added_items > 0:
            logger.info("Found %s new items", added_items)
        logger.info("Done!")

    def update_sections(self, media_items: MediaItemContainer):
        """Update plex library section"""
        for section in self.plex.library.sections():
            for item in media_items:
                if item.type == section.type and item.state in [
                    MediaItemState.DOWNLOADING,
                    MediaItemState.PARTIALLY_DOWNLOADING,
                ]:
                    if not section.refreshing:
                        section.update()
                        logger.info("Updated section %s", section.title)
                        break

    def _create_item(self, item):
        new_item = _map_item_from_data(item, item.type)
        if new_item and item.type == "show":
            for season in item.seasons():
                if season.seasonNumber != 0:
                    new_season = _map_item_from_data(season, "season")
                    if new_season:
                        for episode in season.episodes():
                            new_episode = _map_item_from_data(episode, "episode")
                            if new_episode:
                                new_season.add_episode(new_episode)
                        new_item.add_season(new_season)
        return new_item

    def match_items(
        self, found_items: MediaItemContainer, media_items: MediaItemContainer
    ):
        """Matches items in given mediacontainer that are not in library
        to items that are in library"""
        logger.info("Matching items...")

        items_to_be_removed = []

        for item in media_items:
            library_item = next(
                (
                    library_item
                    for library_item in found_items
                    if item.state != MediaItemState.LIBRARY
                    and (
                        item.type == "movie"
                        and library_item.type == "movie"
                        and item.file_name == library_item.file_name
                        or item.type == "show"
                        and library_item.type == "show"
                        and any(
                            location in item.locations
                            for location in library_item.locations
                        )
                        or item.imdb_id == library_item.imdb_id
                    )
                ),
                None,
            )

            if library_item:
                if self._fix_match(library_item, item):
                    items_to_be_removed.append(library_item)

                self._update_item(item, library_item)

                items_to_be_removed.append(library_item)

        for item in items_to_be_removed:
            found_items.remove(item)

        for item in found_items:
            if item in media_items:
                if item.state == MediaItemState.DOWNLOADING:
                    logger.debug(
                        "Could not match library item %s to any media item", item.title
                    )
                    # media_items.change_state(MediaItemState.ERROR)

        logger.info("Done!")
        return found_items

    def _update_item(self, item, library_item):
        """Internal method to use with match_items
        It does some magic to update media items according to library
        items found"""
        if item.type == "show":
            # library_season_numbers = [s.number for s in library_item.seasons]
            # item_season_numbers = [s.number for s in item.seasons]

            # # Check if any season from item is missing in library_item
            # missing_seasons = [
            #     s for s in item_season_numbers if s not in library_season_numbers
            # ]
            # if missing_seasons:
            #     state = MediaItemState.LIBRARY_ONGOING

            for season_index, season in enumerate(item.seasons):
                matching_library_season = next(
                    (s for s in library_item.seasons if s == season),
                    None,
                )

                if (
                    not matching_library_season
                ):  # if there's no matching season in the library item
                    continue

                # If the current item season has fewer or
                # same episodes as the library item season, replace it
                if len(season.episodes) <= len(matching_library_season.episodes):
                    item.seasons[season_index] = matching_library_season
                else:  # If not, we need to check each episode
                    for episode in season.episodes:
                        matching_library_episode = next(
                            (
                                e
                                for e in matching_library_season.episodes
                                if str(episode.number) in e.get_multi_episode_numbers()
                                or e == episode
                            ),
                            None,
                        )

                        # Replace the episode in item with the one from library_item
                        if matching_library_episode:
                            true_episode_number = episode.number
                            # matching_library_episode.number = episode.number
                            episode_index = season.episodes.index(episode)
                            season.episodes[episode_index] = copy.copy(
                                matching_library_episode
                            )
                            season.episodes[episode_index].number = true_episode_number
                            continue
                        # if the episode is not in library item season, change its state
                        else:
                            pass
                            # season.change_state(MediaItemState.LIBRARY_ONGOING)
                            # state = MediaItemState.LIBRARY_ONGOING

        if item.type == "movie":
            item.set("file_name", library_item.file_name)
        else:
            item.set("locations", library_item.locations)
        item.set("guid", library_item.guid)
        item.set("key", library_item.key)
        item.set("art_url", library_item.art_url)

    def _fix_match(self, library_item, item):
        """Internal method to use in match_items method.
        It gets plex guid and checks if it matches with plex metadata
        for given imdb_id. If it does, it will update the metadata of the plex item."""
        section = next(
            section
            for section in self.plex.library.sections()
            if section.type == item.type
        )
        dummy = section.search(maxresults=1)[0]

        if dummy and not section.refreshing:
            if item.imdb_id:
                try:
                    match = dummy.matches(agent=section.agent, title=item.imdb_id)[0]
                except ReadTimeout:
                    return False
                except IndexError:
                    return False
                if library_item.guid != match.guid:
                    item_to_update = self.plex.fetchItem(library_item.key)
                    item_to_update.fixMatch(match)
                    return True
        return False


def _map_item_from_data(item, item_type):
    """Map plex API data to MediaItemContainer"""
    # Fetch all data from plex API and catch ReadTimeout
    try:
        item_type = getattr(item, "type", None)
        guid = getattr(item, "guid", None)
        genres = getattr(item, "genres", {})
        available_at = getattr(item, "originallyAvailableAt", None)
        title = getattr(item, "title", None)
        year = getattr(item, "year", None)
        if item_type in ["movie", "show"]:
            guids = getattr(item, "guids", [])
        else:
            guids = []
        key = getattr(item, "key", None)
        locations = getattr(item, "locations", [])
        season_number = getattr(item, "seasonNumber", None)
        episode_number = getattr(item, "episodeNumber", None)
        art_url = getattr(item, "artUrl", None)
    except ReadTimeout:
        return None
    imdb_id = None
    if item_type in ["movie", "show"]:
        imdb_id = next(
            (guid.id.split("://")[-1] for guid in guids if "imdb" in guid.id), None
        )
        genres = [genre.tag for genre in genres] or None
    aired_at = None
    if available_at:
        aired_at = available_at.strftime("%Y-%m-%d:%H")
    item = {
        "state": MediaItemState.LIBRARY,
        "title": title,
        "year": year,
        "imdb_id": imdb_id,
        "aired_at": aired_at,
        "genres": genres,
        "guid": guid,
        "key": key,
        "art_url": art_url,
    }
    match item_type:
        case "movie":
            item["file_name"] = os.path.basename(locations[0])
            return_item = Movie(item)
        case "show":
            item["locations"] = [
                location.split("shows\\")[-1] for location in locations
            ]
            return_item = Show(item)
        case "season":
            item["number"] = season_number
            return_item = Season(item)
        case "episode":
            item["number"] = episode_number
            item["file_name"] = os.path.basename(locations[0])
            return_item = Episode(item)
        case _:
            return_item = None
    return return_item
