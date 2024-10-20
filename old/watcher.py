import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.process = subprocess.Popen(self.command, shell=True)

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}. Restarting application...")
            self.start_process()

if __name__ == "__main__":
    path = "."  # Monitor the current directory
    command = "python pataco_bot.py"  # Command to run your application

    event_handler = RestartOnChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()