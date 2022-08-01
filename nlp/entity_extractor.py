import os
from pathlib import Path

import pandas as pd
import spacy
from spacy import displacy
from spacy.lang import en as english
from spacy.tokens import Doc

from path_reference.folder_reference import get_books_path, get_data_path, get_book_entities_path


class BookAnalyser:
    def __init__(self):
        self.NER: english = spacy.load('en_core_web_sm')
        self.all_books: list[os.DirEntry] = [book for book in os.scandir(get_books_path()) if '.txt' in book.name]
        self.all_books.insert(0, None)
        self.current_file = None
        self.current_book = None

    def select_book(self, book_index: int) -> None:
        self.current_file = self.all_books[book_index]
        self.current_book = self.__apply_nlp(self.all_books[book_index])

    def set_book_example(self) -> None:
        book: os.DirEntry = self.all_books[1]
        self.current_book = self.__apply_nlp(book)

    def __apply_nlp(self, input_book: os.DirEntry) -> Doc:
        book_text = open(input_book).read()
        return self.NER(book_text)

    def print_book(self) -> str:
        book = self.current_book
        example = self.__apply_nlp(book)
        return spacy.displacy.render(example[:100], style="ent", jupyter=True, minify=True)

    def __get_book_entities(self) -> pd.DataFrame:
        entity_pot = []

        for index, sentence in enumerate(self.current_book.sents):
            print(index)
            if entity_list := [entity.text for entity in sentence.ents]:
                entity_pot.append({"sentence": sentence, "entities": entity_list})
        return pd.DataFrame(entity_pot)

    def __get_file_tag(self) -> str:
        return f"{self.current_file.name.split('.')[0]}.csv"

    def __existing_file(self) -> bool:
        return Path(get_book_entities_path(), f"{self.__get_file_tag()}").exists()

    def save_book_entities(self) -> None:
        if existing_file := self.__existing_file():
            print(f"File [{self.__get_file_tag()}] already exists")
        else:
            book_entities = self.__get_book_entities()
            book_entities.to_csv(Path(get_book_entities_path(), f"{self.__get_file_tag()}"))


def get_entities_df() -> pd.DataFrame:
    return pd.read_csv(Path(get_book_entities_path(), "entities.csv"))


def __save_entities_df() -> None:
    book_analyser = BookAnalyser()
    book_analyser.select_book(1)
    book_analyser.save_book_entities()
    # df = book_analyser.get_book_entities()
    # df.to_csv(Path(get_entities_path(), "entities.csv"), index=False)


def __main():
    __save_entities_df()


if __name__ == '__main__':
    __main()
