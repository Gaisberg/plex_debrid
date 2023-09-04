"""Threading helper"""
import threading
import time


class ThreadRunner:
    """Thread runner"""

    def __init__(self, target_method, run_interval=30, *args):
        self.target_method = target_method
        self.args = args
        self.run_interval = run_interval  # in seconds
        self.is_running = False
        self.thread = None

    def _run_thread(self, args):
        while self.is_running:
            if args:
                self.target_method(args)
            else:
                self.target_method()
            time.sleep(self.run_interval)

    def start(self):
        """Starts the thread"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run_thread, args=(self.args,))
            self.thread.start()

    def stop(self):
        """Stops the thread"""
        self.is_running = False
        if self.thread:
            self.thread.join()

    def join(self):
        """Joins the thread"""
        return self.thread.join()
