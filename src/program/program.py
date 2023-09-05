"""Program main module"""
import importlib
import inspect
import os
import sys
from utils.logger import logger
from program.media import MediaItemContainer
from program.libraries.plex import Library as Plex


class Program:
    """Program class"""

    def __init__(self):
        self.plex = Plex()

        self.media_items = MediaItemContainer()

        self.content_services = self.__import_modules("src/program/content")
        self.scraping_services = self.__import_modules("src/program/scrapers")
        self.debrid_services = self.__import_modules("src/program/debrid")

        if not os.path.exists("data"):
            os.mkdir("data")

    def run(self):
        """Run the program"""
        self.media_items.load("data/media.pkl")

        self.plex.update_sections(self.media_items)
        self.plex.update_metadata_for_items(self.media_items)
        self.plex.get_new_items(self.media_items)

        # Update content lists
        for content_service in self.content_services:
            content_service.update_items(self.media_items)

        self.plex.match_items(self.media_items)

        for scraper in self.scraping_services:
            scraper.scrape(self.media_items)
        for debrid in self.debrid_services:
            debrid.download(self.media_items)

        self.media_items.save("data/media.pkl")

    def __import_modules(self, folder_path: str) -> list[object]:
        file_list = [
            f[:-3]
            for f in os.listdir(folder_path)
            if f.endswith(".py") and f != "__init__.py"
        ]
        module_path_name = folder_path.split("/")[-1]
        modules = []
        for module_name in file_list:
            module = importlib.import_module(
                f"..{module_name}", f"program.{module_path_name}.{module_name}"
            )
            sys.modules[module_name] = module
            clsmembers = inspect.getmembers(module, inspect.isclass)
            wanted_classes = ["Library", "Content", "Scraper", "Debrid"]
            for name, obj in clsmembers:
                if name in wanted_classes:
                    module = obj()
                    try:
                        # self._setup(module)
                        modules.append(module)
                    except TypeError as exception:
                        logger.error(exception)
                        raise KeyboardInterrupt from exception
        return modules

    # def _setup(self, module):
    #     if not hasattr(module, "settings"):
    #         logger.error(
    #             "%s does not have attribute module.settings,"
    #             + "could not verify needed settings!",
    #             module.__module__,
    #         )
    #         raise TypeError(f"Please set {module.settings} attribute!")
    #     logger.debug("Verifying settings for %s", module.__module__)
    #     for setting, value in module.class_settings.items():
    #         if value == "":
    #             raise TypeError(f"Please set {module.settings}.{setting} value!")
