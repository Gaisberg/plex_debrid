'''
    Main module for the application.
'''
import time
from program.program import Program
from settings.manager import settings_manager
from utils.thread import ThreadRunner

if __name__ == '__main__':
    program = Program(settings_manager)
    runner = ThreadRunner(program.run)
    runner.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        runner.stop()
