# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import dataclasses
import os
from pathlib import Path

import pandas as pd
import spacy
from spacy import displacy
from spacy.lang import en as english
from spacy.tokens import Doc

from path_reference.folder_reference import get_data_path


class BookAnalyser:
    def __init__(self):
        self.NER: english = spacy.load('en_core_web_sm')
        self.all_books: list[os.DirEntry] = [book for book in os.scandir(get_data_path()) if '.txt' in book.name]
        self.current_book = None

    def select_book(self, book_index: int) -> None:
        self.current_book = self.__apply_nlp(self.all_books[book_index])

    def set_book_example(self) -> None:
        book: os.DirEntry = self.all_books[0]
        self.current_book = self.__apply_nlp(book)

    def __apply_nlp(self, input_book: os.DirEntry) -> Doc:
        book_text = open(input_book).read()
        return self.NER(book_text)

    def print_book_example(self) -> str:
        book = self.current_book
        example = self.__apply_nlp(book)
        return spacy.displacy.render(example[:100], style="ent", jupyter=True, minify=True)

    def get_book_entities(self) -> pd.DataFrame:
        entity_pot = []

        for index, sentence in enumerate(self.current_book.sents):
            print(index)
            if entity_list := [entity.text for entity in sentence.ents]:
                entity_pot.append({"sentence": sentence, "entities": entity_list})
        return pd.DataFrame(entity_pot)


def get_entities_df() -> pd.DataFrame:
    return pd.read_csv(Path(get_data_path(), "entities.csv"))


def __save_entities_df() -> None:
    book_analyser = BookAnalyser()
    book_analyser.set_book_example()
    df = book_analyser.get_book_entities()
    forbidden_characters = ["[", "'", "]"]
    df["entities"] = df["entities"].apply(lambda x: [item for item in x if item not in forbidden_characters])
    df.to_csv(Path(get_data_path(), "entities.csv"), index=False)


def __main():
    __save_entities_df()
    # book_analyser = BookAnalyser()
    # book_analyser.set_book_example()
    # aux = book_analyser.get_book_entities()
    # print(aux)


if __name__ == '__main__':
    __main()
