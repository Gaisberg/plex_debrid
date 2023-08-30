from flask import Blueprint


class ProgramController(Blueprint):
    def __init__(self, program):
        super().__init__("program", __name__)
        self.program = program
        self.register_blueprint(self.LibraryController(self.program.library_services))
        self.register_blueprint(self.ContentController(self.program.content_services))
        # self.register_blueprint(self.ScrapingController(self.program.scraping_instances))
        # self.register_blueprint(self.DebridController(self.program.debrid_instances))

    class LibraryController(Blueprint):
        def __init__(self, instances: list):
            super().__init__("library", __name__)

            self.instances = instances
            self.add_url_rule("/hello", methods=["GET"], view_func=self.hello_world)
            self.add_url_rule(
                "/sup", methods=["GET"], view_func=self.get_class_settings
            )

        def get_instance(self, settings_name: str):
            return next(
                service
                for service in self.instances
                if service.settings == settings_name
            )

        def hello_world(self):
            return "Hello, World!"

        def get_class_settings(self):
            return self.get_instance("library_plex").class_settings

    class ContentController(Blueprint):
        def __init__(self, instances: list):
            super().__init__("content", __name__)
            self.instances = instances
            self.add_url_rule(
                "/lol", methods=["GET"], view_func=self.get_class_settings
            )

        def get_instance(self, settings_name: str):
            return next(
                service
                for service in self.instances
                if service.settings == settings_name
            )

        def get_class_settings(self):
            return self.get_instance("content_mdblist").class_settings
