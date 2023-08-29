class MediaItem:
    '''MediaItem class'''

    STATE_UNKNOWN = -1
    STATE_IN_LIBRARY = 0
    STATE_IN_CONTENT_SERVICE = 1
    STATE_SCRAPED = 2
    STATE_IN_DOWNLOAD = 3

    def __init__(self, item, state=STATE_UNKNOWN):
        self.title = item["title"]
        self.type = item["type"]
        self.release_year = item["release_year"]
        self.state = state
        if "imdb_id" in item:
            self.imdb_id = item["imdb_id"]

    def __eq__(self, other):
        #TODO for shows and episodes
        return self.title == other.title and self.type == other.type

    def __iter__(self):
        for attr, _ in vars(self).items():
            yield attr
