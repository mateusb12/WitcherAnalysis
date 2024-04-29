import json
import os
import time
from pathlib import Path

from spacy.tokens import Doc

from source.path_reference.folder_reference import get_books_path, get_book_entities_path, get_cache_path


def list_all_book_files(input_series: str) -> list[Path]:
    book_path = Path(get_books_path(), f"{input_series}_books")
    return list(book_path.glob('*.txt'))


def get_entities_file_path(input_series: str) -> Path:
    return Path(get_book_entities_path(), f"{input_series}_books_entities")


def extract_entities(sentence):
    return [entity.text for entity in sentence.ents]


def cache_file_exists(file_location: Path) -> bool:
    book_name = file_location.name.split('.')[0]
    cache_path = Path(get_cache_path(), f"{book_name}.bin")
    return cache_path.exists()


def save_cache_file(file_location: Path, doc: Doc):
    book_name = file_location.name.split('.')[0]
    cache_file_location = Path(get_cache_path(), f"{book_name}.bin")
    doc.to_disk(cache_file_location)


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
