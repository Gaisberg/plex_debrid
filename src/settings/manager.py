'''Settings manager'''
import json
import os
from sys import platform
import subprocess
from utils.logger import logger

class SettingsManager:
    '''Class that handles settings'''

    def __init__(self):
        self.filename = 'settings.json'
        self.config_dir = '.'
        self.settings_file = os.path.join(self.config_dir, self.filename)
        self.settings = {}
        self.load()

    def load(self):
        '''Load settings from file'''
        if not os.path.exists(self.filename):
            if platform == "win32":
                subprocess.call(f'copy {os.path.join(os.path.dirname(__file__), "default_settings.json")} {os.path.join(self.config_dir, self.filename)}', shell=True)
            elif platform == "linux":
                subprocess.call(f'cp {os.path.join(os.path.dirname(__file__), "default_settings.json")} {os.path.join(self.config_dir, self.filename)}')
            logger.debug('Settings file not found, using default settings')
        with open(self.filename, 'r', encoding='utf-8') as file:
            self.settings = json.loads(file.read())
        logger.debug('Settings loaded from %s', self.filename)


    def save(self):
        '''Save settings to file'''
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.settings, file, indent=4)

        logger.debug('Settings saved to %s', self.filename)

    def get(self, key):
        '''Get setting with key'''
        if key in self.settings:
            value = self.settings[key]
            logger.debug('Get (%s) returned: %s', key, value)
            return value
        return None

    def set(self, key, value):
        '''Set setting value with key'''
        if key in self.settings:
            logger.debug('Setting (%s) to (%s)', key, value)
            self.settings[key] = value

settings_manager = SettingsManager()
