import os
from pathlib import Path

import pandas as pd
import spacy
from spacy import displacy
from spacy.lang import en as english
from spacy.tokens import Doc

from path_reference.folder_reference import get_books_path, get_data_path, get_book_entities_path


def get_all_books(input_series: str) -> list[os.DirEntry]:
    book_path = get_books_path()
    series_book_path = Path(book_path, f"{input_series}_books")
    aux = [book for book in os.scandir(series_book_path) if '.txt' in book.name]
    aux.insert(0, None)
    return aux


def get_entities_location(input_series: str) -> Path:
    return Path(get_book_entities_path(), f"{input_series}_books_entities")


class BookAnalyser:
    def __init__(self, series: str = "witcher"):
        self.series_tag = series
        self.NER: english = spacy.load('en_core_web_sm')
        self.all_books: list[os.DirEntry] = get_all_books(series)
        self.current_file = None
        self.current_book = None
        self.book_dict = self.get_book_dict()

    def set_new_series(self, input_series: str):
        self.series_tag = input_series
        self.all_books = get_all_books(input_series)
        self.book_dict = self.get_book_dict()

    def get_book_dict(self) -> dict:
        return {index: book.name.split('.')[0] for index, book in enumerate(self.all_books) if index != 0}

    def select_book(self, book_index: int) -> None:
        self.current_file = self.all_books[book_index]
        self.current_book = self.__apply_nlp(self.all_books[book_index])
        print(f"Selected book → {self.current_file.name}")

    def set_book_example(self) -> None:
        book: os.DirEntry = self.all_books[1]
        self.current_book = self.__apply_nlp(book)

    def __apply_nlp(self, input_book: os.DirEntry) -> Doc:
        book_text = open(input_book, encoding="utf8").read()
        return self.NER(book_text)

    def print_book(self) -> str:
        book = self.current_book
        example = self.__apply_nlp(book)
        return spacy.displacy.render(example[:100], style="ent", jupyter=True, minify=True)

    def __get_book_entities(self) -> pd.DataFrame:
        entity_pot = []
        size = len(list(self.current_book.sents))

        for index, sentence in enumerate(self.current_book.sents):
            print(f"Processing sentence {index} of {size}")
            if entity_list := [entity.text for entity in sentence.ents]:
                entity_pot.append({"sentence": sentence, "entities": entity_list})
        return pd.DataFrame(entity_pot)

    def __get_file_tag(self) -> str:
        return f"{self.current_file.name.split('.')[0]}.csv"

    def __existing_file(self) -> bool:
        return Path(get_entities_location(self.series_tag), f"{self.__get_file_tag()}").exists()

    def get_book_entity_df(self) -> pd.DataFrame:
        if existing_file := self.__existing_file():
            print(f"File [{self.__get_file_tag()}] already exists")
            ref = Path(get_entities_location(self.series_tag), f"{self.__get_file_tag()}")
            return pd.read_csv(ref)
        else:
            book_entities = self.__get_book_entities()
            output_location = Path(get_entities_location(self.series_tag), f"{self.__get_file_tag()}")
            self.handle_new_folder(output_location)
            book_entities.to_csv(output_location, index=False)
            return book_entities

    @staticmethod
    def handle_new_folder(output_location):
        """ Creates a new folder if it doesn't exist """
        output_folder = output_location.parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
            Path(output_folder, "__init__.py").touch()


def __save_entities_df():
    book_analyser = BookAnalyser(series="harry_potter")
    book_analyser.select_book(1)
    aux = book_analyser.get_book_entity_df()
    return 0


def __main():
    __save_entities_df()


if __name__ == '__main__':
    __main()
