"""
    Main module for the application.
"""
import time

from flask import Flask
from program.program import Program
from utils.thread import ThreadRunner
from controllers.controller import ProgramController

if __name__ == "__main__":
    app = Flask(__name__)
    program = Program()
    app.register_blueprint(ProgramController(program))
    runner = ThreadRunner(program.run, run_interval=5)
    runner.start()
    app.run(host="localhost", port=8080)
    # TODO Disable flask logging

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        runner.stop()
