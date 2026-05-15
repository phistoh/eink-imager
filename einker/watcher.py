import logging
import shutil
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from queue import Queue

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from einker.confparser import get_config
from einker.file_handling import scan_image_consistency
from einker.image_processing import extract_features, process_image, validate_image
from einker.metadata import add_image, add_image_features, init_db

logger = logging.getLogger(__name__)
image_queue: Queue[Path] = Queue()
CONFIG = get_config()


def wait_until_complete(path: Path, timeout: int = 60) -> None:
    previous_size = -1
    start_time = time.monotonic()

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

        if time.monotonic() - start_time > timeout:
            raise TimeoutError(f"Timed out waiting for {path}")


def process_file(path: Path) -> None:
    if not path.exists():
        return

    wait_until_complete(path)

    new_file_id = f"{uuid.uuid4().hex}"
    new_file_name = f"{new_file_id}{path.suffix}"

    valid_image, reason = validate_image(path)

    if not valid_image:
        logger.info("Skipping %s (%s)", path, reason)
        shutil.move(path, CONFIG.paths.failed_dir / new_file_name)
        return

    process_image(
        source=path,
        destination=CONFIG.paths.image_dir / new_file_name,
        size=(800, 480),
    )

    destination = CONFIG.paths.processed_dir / new_file_name
    shutil.move(path, destination)

    add_image(
        image_id=new_file_id,
        original_name=path.name,
        processed_name=new_file_name,
        created_at=datetime.now().isoformat(),
    )

    features = extract_features(destination)
    add_image_features(new_file_id, features)

    logger.info("Moved processed file to %s", destination)


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix.lower() != ".jpg":
            return

        logger.info("Queued file: %s", path)
        image_queue.put(path)


def worker():
    while True:
        path = image_queue.get()

        try:
            logger.info("Processing file: %s", path)
            process_file(path)
        except Exception:
            logger.exception("Failed processing %s", path)

        image_queue.task_done()


def process_existing_files() -> None:
    for path in sorted(CONFIG.paths.watch_dir.glob("*.jpg")):
        logger.info("Queued file: %s", path)
        image_queue.put(path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    init_db()
    scan_image_consistency()

    CONFIG.paths.processed_dir.mkdir(exist_ok=True)

    threading.Thread(
        target=worker,
        daemon=True,
        name="file-watcher",
    ).start()

    process_existing_files()

    observer = Observer()
    observer.schedule(ImageHandler(), str(CONFIG.paths.watch_dir), recursive=False)
    observer.start()

    logger.info("Watcher started")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
        observer.join()
