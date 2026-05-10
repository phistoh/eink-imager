import shutil
import threading
import time
import uuid
from pathlib import Path
from queue import Queue

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import config

image_queue = Queue()


def wait_until_complete(path: Path) -> None:
    previous_size = -1

    while True:
        try:
            current_size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(1)
            continue

        if current_size == previous_size:
            return

        previous_size = current_size
        time.sleep(1)


def process_file(path: Path) -> None:
    if not path.exists():
        return
    wait_until_complete(path)

    # TODO process image
    print(path)

    destination = config.PROCESSED_DIR / f"{uuid.uuid4().hex}{path.suffix}"
    shutil.move(path, destination)


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() != ".jpg":
            return

        image_queue.put(path)


def worker():
    while True:
        path = image_queue.get()

        try:
            process_file(path)
        except Exception as e:
            print(f"Failed processing {path}: {e}")

        image_queue.task_done()


def process_existing_files() -> None:
    for path in sorted(config.WATCH_DIR.glob("*.jpg")):
        image_queue.put(path)


def start_watcher():
    process_existing_files()
    observer = Observer()
    observer.schedule(ImageHandler(), str(config.WATCH_DIR), recursive=False)
    observer.start()

    threading.Thread(target=worker, daemon=True).start()
