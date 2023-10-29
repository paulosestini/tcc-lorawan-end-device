import time
import pandas as pd
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MatrixHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_position = 0
        self.buffer = ""

    def process(self, event):
        if event.event_type == 'modified':
            with open('output.txt', 'r') as f:
                f.seek(self.last_position)
                new_data = f.read()
                self.last_position = f.tell()

                self.buffer += new_data
                while "START_MATRIX\n" in self.buffer and "END_MATRIX\n" in self.buffer:
                    start = self.buffer.find("START_MATRIX\n") + len("START_MATRIX\n")
                    end = self.buffer.find("END_MATRIX\n")
                    matrix_str = self.buffer[start:end].strip()
                    self.buffer = self.buffer[end + len("END_MATRIX\n"):]

                    matrix = [list(map(float, row.split())) for row in matrix_str.split('\n') if row.strip()]
                    df = pd.DataFrame(matrix)
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    df.to_csv(f'matrices/matrix_{timestamp}.csv', index=False, header=False)

    def on_modified(self, event):
        self.process(event)

if __name__ == "__main__":
    event_handler = MatrixHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
