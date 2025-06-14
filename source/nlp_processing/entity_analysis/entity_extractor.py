import os
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from spacy.tokens import Doc
import spacy
from utils.entity_utils import extract_entities, print_progress, get_entities_file_path
from utils.folder_utils import handle_new_folder


class EntityExtractor:
    """This class is used to extract entities from a book.
     It analyses each book and creates an entities.csv file in the book_entities folder."""

    def __init__(self):
        self.current_book_entities: Doc = None
        self.current_file: Optional[os.DirEntry] = None
        self.series_tag: str = "harry_potter"

    def set_information(self, book: Doc, file: Path, series: str):
        # Ensure sentence boundaries are set for the Doc
        if not book.has_annotation("SENT_START"):
            # Load a blank model just to add sentencizer if needed
            nlp = spacy.blank(book.lang if hasattr(book, 'lang') else 'en')
            if 'sentencizer' not in nlp.pipe_names:
                nlp.add_pipe('sentencizer')
            book = nlp(book.text)
        self.current_book_entities = book
        self.current_file = file
        self.series_tag = series

    def setup_entity_data(self, entities: Doc):
        self.current_book_entities = entities

    def extract_book_entities(self) -> pd.DataFrame:
        entity_pot = []
        size = len(list(self.current_book_entities.sents))
        time_start = time.time()

        for index, sentence in enumerate(self.current_book_entities.sents):
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
        book_entities: pd.DataFrame = self.extract_book_entities()
        output_location = Path(get_entities_file_path(self.series_tag), f"{self.__get_file_tag()}")
        handle_new_folder(output_location)
        book_entities.to_csv(output_location, index=False)
        return book_entities

    def _read_existing_book_entity_table(self) -> pd.DataFrame:
        print(f"- -             File [{self.__get_file_tag()}] already exists")
        ref = Path(get_entities_file_path(self.series_tag), f"{self.__get_file_tag()}")
        return pd.read_csv(ref)
