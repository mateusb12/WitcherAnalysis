import os
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from spacy import displacy
from spacy.tokens import Doc

from source.nlp_processing.model_loader import load_nlp_model
from source.nlp_processing.text_processor import TextProcessor
from source.utils.entity_utils import list_all_book_files, extract_entities, print_progress, get_entities_file_path, \
    cache_file_exists, save_cache_file
from source.utils.folder_utils import handle_new_folder


class EntityExtractor:
    """This class is used to extract entities from a book.
     It analyses each book and creates an entities.csv file in the book_entities folder."""

    def __init__(self, nlp_model, series_tag: str = "witcher"):
        self.text_processor = TextProcessor(nlp_model)
        self.series_tag = series_tag
        self.all_books: list[Path] = list_all_book_files(series_tag)
        self.current_file: Optional[os.DirEntry] = None
        self.current_book: Optional[Doc] = None
        self.book_names_dict = self.generate_book_dict()

    def set_series(self, input_series: str):
        self.series_tag = input_series
        self.all_books = list_all_book_files(input_series)
        self.book_names_dict = self.generate_book_dict()

    def generate_book_dict(self) -> dict:
        return {index: book.name.split('.')[0] for index, book in enumerate(self.all_books) if index != 0}

    def select_book(self, book_index: int) -> None:
        self.current_file = self.all_books[book_index]
        self.current_book = self.text_processor.analyze_book(self.current_file)
        print(f"Selected book → {self.current_file.name}")

    def set_book_example(self) -> None:
        book: Path = self.all_books[1]
        self.current_book = self.text_processor.analyze_book(book)

    def print_book(self) -> str:
        book = self.current_book
        return displacy.render(book[:100], style="ent", jupyter=True, minify=True)

    def __extract_book_entities(self) -> pd.DataFrame:
        entity_pot = []
        size = len(list(self.current_book.sents))
        time_start = time.time()

        for index, sentence in enumerate(self.current_book.sents):
            print_progress(index, size, time_start)
            entity_list = extract_entities(sentence)
            if entity_list:
                entity_pot.append({"sentence": sentence, "entities": entity_list})
        return pd.DataFrame(entity_pot)

    def get_book_entity_table(self) -> pd.DataFrame:
        if not self.__existing_entity_file():
            print("File not found")
            return self._create_new_book_entity_table()
        return self._read_existing_book_entity_table()

    def __get_file_tag(self) -> str:
        return f"{self.current_file.name.split('.')[0]}.csv"

    def __existing_entity_file(self) -> bool:
        return Path(get_entities_file_path(self.series_tag), f"{self.__get_file_tag()}").exists()

    def _create_new_book_entity_table(self) -> pd.DataFrame:
        print("Book entity not found. Processing a new one...")
        book_entities: pd.DataFrame = self.__extract_book_entities()
        output_location = Path(get_entities_file_path(self.series_tag), f"{self.__get_file_tag()}")
        handle_new_folder(output_location)
        book_entities.to_csv(output_location, index=False)
        return book_entities

    def _read_existing_book_entity_table(self) -> pd.DataFrame:
        print(f"File [{self.__get_file_tag()}] already exists")
        ref = Path(get_entities_file_path(self.series_tag), f"{self.__get_file_tag()}")
        return pd.read_csv(ref)


def __save_entities_df():
    model = load_nlp_model()
    book_analyser = EntityExtractor(nlp_model=model, series_tag="harry_potter")
    book_analyser.select_book(1)
    aux2 = book_analyser.print_book()
    aux = book_analyser.get_book_entity_table()
    return 0


def __main():
    __save_entities_df()


if __name__ == '__main__':
    __main()
