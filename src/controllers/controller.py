""" Program controller """
from flask import Blueprint


class ProgramController(Blueprint):
    """Program controller blueprint"""

    def __init__(self, program):
        super().__init__("program", __name__)
        self.program = program
        self.register_blueprint(self.PlexController(self.program.plex))
        self.register_blueprint(self.ContentController(self.program.content_services))
        # self.register_blueprint(self.ScrapingController(self.program.scraping_instances))
        # self.register_blueprint(self.DebridController(self.program.debrid_instances))
        self.add_url_rule("/states", methods=["GET"], view_func=self.get_all_items)

    def get_all_items(self):
        """Get all media items"""
        return self.program.media_items.items

    class PlexController(Blueprint):
        """Plex controller blueprint"""

        def __init__(self, plex):
            super().__init__("library", __name__)
            self.plex = plex
            self.add_url_rule("/hello", methods=["GET"], view_func=self.hello_world)

        def hello_world(self):
            """Hello world"""
            return "Hello, World!"

    class ContentController(Blueprint):
        """Content controller blueprint"""

        def __init__(self, instances: list):
            super().__init__("content", __name__)
            self.instances = instances
            self.add_url_rule("/lol", methods=["GET"], view_func=self.get_mdb_settings)

        def _get_instance(self, settings_name: str):
            return next(
                service
                for service in self.instances
                if service.settings == settings_name
            )

        def get_mdb_settings(self):
            """Get mdb list content service settings"""
            return self._get_instance("content_mdblist").class_settings
