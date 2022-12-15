import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
from spacy import displacy
from spacy.lang import en as english
from spacy.pipeline import Sentencizer
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
    """This class is used to extract entities from a book.
     It analyses each book and creates an entities.csv file in the book_entities folder."""
    def __init__(self, series: str = "witcher"):
        self.series_tag = series
        self.nlp: english = spacy.load('en_core_web_sm')
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
        self.current_book = self.__apply_nlp(self.current_file)
        print(f"Selected book → {self.current_file.name}")

    def set_book_example(self) -> None:
        book: os.DirEntry = self.all_books[1]
        self.current_book = self.__apply_nlp(book)

    def __apply_nlp(self, input_book: os.DirEntry) -> Doc:
        input_book_location = input_book.path
        with open(input_book_location, encoding="utf8") as f:
            book_text = f.read()
            text_size = len(book_text)
            if text_size <= 1000000:
                return self.nlp(book_text)
            print("Big file detected. Splitting...")
            return self.__handle_big_file(book_text)

    def __handle_big_file(self, file_content: str) -> Doc:
        """Natural language processing modules cannot handle strings over than 1 million characters.
         This function splits the large file into smaller chunks and applies nlp to each chunk.
         Then it merges everything into a single Doc structure"""
        self.nlp.disable_pipes()
        self.nlp.add_pipe("sentencizer")
        self.nlp.enable_pipe("sentencizer")
        chunk_size = 500000
        print("[Big file analysis]   Getting text chunks (1/3)")
        text_chunks = [file_content[i:i + chunk_size] for i in range(0, len(file_content), chunk_size)]
        doc_list = list(self.nlp.pipe(text_chunks))
        print("[Big file analysis]   Generating single doc (2/3)")
        single_doc = Doc(self.nlp.vocab, words=[token.text for doc in doc_list for token in doc])
        print("[Big file analysis]   Analysing single doc (3/3)")
        for i, token in enumerate(single_doc):
            if token.text.startswith(".") or token.text.startswith("!") or token.text.startswith("?"):
                single_doc[i].is_sent_start = True
        return single_doc

    def print_book(self) -> str:
        book = self.current_book
        # example = self.__apply_nlp(book)
        return spacy.displacy.render(book[:100], style="ent", jupyter=True, minify=True)

    def __get_book_entities(self) -> pd.DataFrame:
        entity_pot = []
        size = len(list(self.current_book.sents))
        time_start = time.time()

        for index, sentence in enumerate(self.current_book.sents):
            percentage = round((index / size) * 100, 2)
            time_elapsed_seconds = round(time.time() - time_start, 2)
            speed = index / time_elapsed_seconds if time_elapsed_seconds != 0 else 1
            remaining_sentences = size - index
            remaining_seconds = round(remaining_sentences / speed, 2) if speed != 0 else 0
            eta = time_start + remaining_seconds
            eta_str = time.strftime("%H:%M:%S", time.localtime(eta))
            if index % 10 == 0:
                print(f"Processing sentence {index} of {size} ({percentage}%), speed: {round(speed, 2)} sentences/s,"
                      f"ETA {eta_str}")
            entities = [entity.text for entity in sentence.ents]
            if entity_list := entities:
                entrance = {"sentence": sentence, "entities": entity_list}
                entity_pot.append(entrance)
        return pd.DataFrame(entity_pot)

    def __get_file_tag(self) -> str:
        return f"{self.current_file.name.split('.')[0]}.csv"

    def __existing_file(self) -> bool:
        return Path(get_entities_location(self.series_tag), f"{self.__get_file_tag()}").exists()

    def get_book_entity_df(self) -> pd.DataFrame:
        if not self.__existing_file():
            return self._create_book_entity_df()
        print(f"File [{self.__get_file_tag()}] already exists")
        ref = Path(get_entities_location(self.series_tag), f"{self.__get_file_tag()}")
        return pd.read_csv(ref)

    def _create_book_entity_df(self):
        print("Book entity not found. Processing a new one...")
        book_entities = self.__get_book_entities()
        output_location = Path(get_entities_location(self.series_tag), f"{self.__get_file_tag()}")
        self.handle_new_folder(output_location)
        book_entities.to_csv(output_location, index=False)
        return book_entities

    @staticmethod
    def handle_new_folder(output_location):
        """ Create a new output folder if it doesn't already exist, with an __init__.py` file inside. """
        output_folder = output_location.parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
            Path(output_folder, "__init__.py").touch()


def __save_entities_df():
    book_analyser = BookAnalyser(series="harry_potter")
    book_analyser.select_book(1)
    aux2 = book_analyser.print_book()
    aux = book_analyser.get_book_entity_df()
    return 0


def __main():
    __save_entities_df()


if __name__ == '__main__':
    __main()
