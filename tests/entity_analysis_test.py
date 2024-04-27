import os
import unittest
from pathlib import Path

import pandas as pd

from nlp_processing.entity_extractor import EntityExtractor
from path_reference.folder_reference import get_books_entities_path, get_books_path


class TestBookAnalyser(unittest.TestCase):
    def setUp(self):
        self.analyser = EntityExtractor(series="harry_potter")

    def test_set_new_series(self):
        # Test that set_new_series() correctly sets the series_tag and all_books attributes
        self.analyser.set_new_series("harry_potter")
        self.assertEqual(self.analyser.series_tag, "harry_potter")
        books_path = get_books_path()
        books_folder = os.listdir(Path(books_path, "harry_potter_books"))
        harry_potter_books_amount = len([item for item in books_folder if str(item).endswith(".txt")]) + 1
        self.assertEqual(len(self.analyser.all_books), harry_potter_books_amount)

    def test_get_book_dict(self):
        # Test that get_book_dict() returns the correct book dictionary
        self.assertEqual(self.analyser.get_book_dict(), {1: "1 The Philosopher's Stone",
                                                         2: "2 The Chamber of Secrets",
                                                         3: "3 The Prisoner of Azkaban",
                                                         4: "4 The Goblet of Fire",
                                                         5: "5 The Order of the Phoenix",
                                                         6: "6 The Half Blood Prince",
                                                         7: "7 The Deathly Hallows"})

    def test_set_book_example(self):
        # Test that set_book_example() correctly sets the current_book attribute
        self.analyser.set_book_example()
        self.assertIsNotNone(self.analyser.current_book)


if __name__ == '__main__':
    unittest.main()
