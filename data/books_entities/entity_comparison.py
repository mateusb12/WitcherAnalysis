import os
import random
from pathlib import Path

import pandas as pd

from path_reference.folder_reference import get_books_entities_path


def load_harry_potter_book():
    """This function choses a random .csv from harry_potter_book_entities folder and returns it as a dataframe"""
    path = Path(get_books_entities_path(), "harry_potter_books_entities")
    files = [item for item in os.listdir(path) if str(item).endswith(".csv")]
    random_book = random.choice(files)
    return pd.read_csv(Path(path, random_book))


def load_witcher_book():
    """This function choses a random .csv from witcher_book_entities folder and returns it as a dataframe"""
    path = Path(get_books_entities_path(), "witcher_books_entities")
    files = [item for item in os.listdir(path) if str(item).endswith(".csv")]
    random_book = random.choice(files)
    return pd.read_csv(Path(path, random_book))


def __main():
    test = load_harry_potter_book()
    test2 = load_witcher_book()
    return


if __name__ == '__main__':
    __main()
