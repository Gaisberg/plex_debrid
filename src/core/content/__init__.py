""" This module is responsible for getting media items from content providers"""

from core.content import mdblist, overseerr
from core.trakt import Trakt

content_providers = [mdblist.Mdblist(), overseerr.Overseerr()]

trakt = Trakt()
ImdbIds = set()


def get_items():
    """Get items from content providers"""
    for provider in content_providers:
        ImdbIds.update(provider.get_items())
    return trakt.create_items(ImdbIds)
