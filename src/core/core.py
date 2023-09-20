"""Program main module"""
import os
from core.content import get_items as get_items_from_content_providers
# from utils.logger import logger
from core.media import MediaItemContainer
from core.plex import Library as Plex
from core.realdebrid import Debrid as RealDebrid
from core.scrapers.torrentio import Scraper as Torrentio


class Core:
    """Program class"""

    def __init__(self):
        self.plex = Plex()
        self.debrid = RealDebrid()
        self.torrentio = Torrentio()
        self.media_items = MediaItemContainer()

        if not os.path.exists("data"):
            os.mkdir("data")

    def run(self):
        """Run the program"""
        self.media_items.load("data/media.pkl")
        self.media_items.extend(get_items_from_content_providers())

        self.plex.update_sections(self.media_items)
        self.plex.update_items(self.media_items)

        self.torrentio.scrape(self.media_items)
        self.debrid.download(self.media_items)

        self.media_items.save("data/media.pkl")

    # def __import_modules(self, folder_path: str) -> list[object]:
    #     file_list = [
    #         f[:-3]
    #         for f in os.listdir(folder_path)
    #         if f.endswith(".py") and f != "__init__.py"
    #     ]
    #     module_path_name = folder_path.split("/")[-1]
    #     modules = []
    #     for module_name in file_list:
    #         module = importlib.import_module(
    #             f"..{module_name}", f"program.{module_path_name}.{module_name}"
    #         )
    #         sys.modules[module_name] = module
    #         clsmembers = inspect.getmembers(module, inspect.isclass)
    #         wanted_classes = ["Content"]
    #         for name, obj in clsmembers:
    #             if name in wanted_classes:
    #                 module = obj()
    #                 try:
    #                     # self._setup(module)
    #                     modules.append(module)
    #                 except TypeError as exception:
    #                     logger.error(exception)
    #                     raise KeyboardInterrupt from exception
    #     return modules

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
