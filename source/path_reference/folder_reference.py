import sys
from pathlib import Path

ref = Path(__file__).parent.parent


def get_data_path() -> Path:
    return Path(ref, 'data')


def get_books_entities_path() -> Path:
    return Path(get_data_path(), 'books_entities')


def get_book_characters_path() -> Path:
    return Path(get_data_path(), 'books_characters')


def get_books_path() -> Path:
    return Path(get_data_path(), 'books')


def get_book_entities_path() -> Path:
    return Path(get_data_path(), 'books_entities')


def get_book_importance_path() -> Path:
    return Path(get_data_path(), 'books_importance')


def get_webscrapping_path() -> Path:
    return Path(ref, 'webscrapping')


def get_driver_path() -> Path:
    return get_webscrapping_path() / 'geckodriver.exe'


def get_runner_path():
    return Path(ref, 'scripts')


def get_book_graphs_path():
    return Path(get_runner_path(), 'book_graphs')


def get_cache_path() -> Path:
    return Path(get_data_path(), 'cache')
