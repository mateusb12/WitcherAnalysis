import itertools

import numpy as np
import pytest
from pathlib import Path
import pandas as pd

from book_processing.entity_filter import EntityFilter
from path_reference.folder_reference import get_data_path, get_books_entities_path, get_book_characters_path, \
    get_books_path


class BookTest:
    def __init__(self, book_name: str, series: str = "witcher"):
        self.book_name = book_name
        self.series = series

        self.book_df = None
        self.entity_df = None

        self.__load_data()
        self.ef = EntityFilter(series=self.series)

    def __load_data(self):
        book_path = Path(get_books_path(), f"{self.series}_books", f"{self.book_name}.txt")
        entity_path = Path(get_books_entities_path(), f"{self.series}_books_entities", f"{self.book_name}.csv")
        self.entity_df = pd.read_csv(entity_path, encoding="utf-8")

    def set_entity_df(self):
        self.ef.set_entity_df(self.entity_df)

    def get_filtered_df(self):
        return self.ef.export_filtered_dataframe()


def get_last_witcher_unique_characters() -> list[str]:
    b = BookTest("1 The Last Wish")
    b.set_entity_df()
    filtered_df = b.get_filtered_df()
    values = filtered_df["character_entities"].values
    flattened_values = list(itertools.chain(*values))
    return list(set(flattened_values))


def get_harry_potter_unique_characters() -> list[str]:
    b = BookTest("1 The Philosopher's Stone", series="harry_potter")
    b.set_entity_df()
    filtered_df = b.get_filtered_df()
    values = filtered_df["character_entities"].values
    flattened_values = list(itertools.chain(*values))
    return list(set(flattened_values))


def test_witcher_main_characters():
    """This function tests if some main characters are present in the entitites"""
    unique_entities = get_last_witcher_unique_characters()
    expected = ["Geralt", "Triss"]
    for character in expected:
        assert character in unique_entities


def test_harry_potter_main_characters():
    """This function tests if some main characters are present in the entitites"""
    unique_entities = get_harry_potter_unique_characters()
    expected = ["Harry", "Hermione", "Ron"]
    for character in expected:
        assert character in unique_entities
