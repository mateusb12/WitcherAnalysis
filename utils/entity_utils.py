import time
from pathlib import Path

from path_reference.folder_reference import get_books_path, get_book_entities_path


def list_all_book_files(input_series: str) -> list[Path]:
    book_path = Path(get_books_path(), f"{input_series}_books")
    return list(book_path.glob('*.txt'))


def get_entities_file_path(input_series: str) -> Path:
    return Path(get_book_entities_path(), f"{input_series}_books_entities")


def extract_entities(sentence):
    return [entity.text for entity in sentence.ents]


def print_progress(index, size, time_start):
    percentage = round((index / size) * 100, 2)
    time_elapsed_seconds = round(time.time() - time_start, 2)
    speed = index / time_elapsed_seconds if time_elapsed_seconds != 0 else 1
    remaining_sentences = size - index
    remaining_seconds = round(remaining_sentences / speed, 2) if speed != 0 else 0
    eta = time_start + remaining_seconds
    eta_str = time.strftime("%H:%M:%S", time.localtime(eta))
    if index % 10 == 0:
        print(
            f"Processing sentence {index} of {size} ({percentage}%), speed: {round(speed, 2)} sentences/s, ETA {eta_str}")