'''Logging utils'''
import datetime
import logging
import os


class Logger(logging.Logger):
    '''Logging class'''
    def __init__(self, file_name):
        super().__init__(file_name)
        formatter = logging.Formatter('[%(asctime)s | %(levelname)s] %(module)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = logging.FileHandler(os.path.join('logs', file_name))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.addHandler(file_handler)
        self.addHandler(console_handler)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
logger = Logger(f"plex_debrid-{timestamp}.log")
