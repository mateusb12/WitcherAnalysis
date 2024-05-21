import json
import os
import time
from pathlib import Path

import pandas as pd
import requests
from django.urls import reverse
from spacy.tokens import Doc

from source.data.cache.cache_loader import existing_nlp_cache, NLP_CACHE_PATH
from source.path_reference.folder_reference import get_books_path, get_book_entities_path, get_nlp_cache_path


def list_all_book_files(input_series: str) -> list[Path]:
    book_path = Path(get_books_path(), f"{input_series}_books")
    return list(book_path.glob('*.txt'))


def get_entities_file_path(input_series: str) -> Path:
    return Path(get_book_entities_path(), f"{input_series}_books_entities")


def extract_entities(sentence):
    return [entity.text for entity in sentence.ents]


def cache_file_exists(file_location: Path) -> bool:
    book_name = file_location.name.split('.')[0]
    filename = f"{book_name}.bin"
    return existing_nlp_cache(filename)


def save_cache_file(file_location: Path, doc: Doc):
    book_name = file_location.name.split('.')[0]
    cache_file_location = Path(NLP_CACHE_PATH, f"{book_name}.bin")
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
            f"Processing sentence {index} of {size} ({percentage}%), speed: {round(speed, 2)} sentences/s,"
            f" ETA {eta_str}")
        progress_bar_callback(percentage)


def progress_bar_callback(percentage):
    progress_url = reverse('progress_update_view')
    full_url = 'http://127.0.0.1:8000' + progress_url
    requests.post(full_url, data={'progress': percentage})


def cast_to_str(list_obj: list) -> str:
    return str(list_obj)


def convert_to_list(input_str: str) -> list[str]:
    if isinstance(input_str, list):
        input_str = cast_to_str(input_str)
    forbidden_characters = ["[", "'", "]"]
    for c in forbidden_characters:
        input_str = input_str.replace(c, "")
    return input_str.split(", ")


def filter_entity_df(entity_list: str, characters_df: pd.DataFrame):
    entity_pot = convert_to_list(entity_list)
    full_names = characters_df["character"].tolist()
    first_names = characters_df["character_first_name"].tolist()
    return [x for x in entity_pot if x in first_names or x in full_names]
