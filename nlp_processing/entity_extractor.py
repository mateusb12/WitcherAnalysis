import os
import time
from pathlib import Path
from typing import Optional

import pandas as pd
from spacy import displacy
from spacy.tokens import Doc

from nlp_processing.model_loader import load_nlp_model
from utils.entity_utils import list_all_book_files, get_entities_file_path, extract_entities, print_progress
from utils.folder_utils import handle_new_folder

CHUNK_SIZE = 500000
TEXT_SIZE = 1000000

class EntityExtractor:
    """This class is used to extract entities from a book.
     It analyses each book and creates an entities.csv file in the book_entities folder."""
    def __init__(self, nlp_model, series_tag: str = "witcher"):
        self.nlp = nlp_model
        self.series_tag = series_tag
        self.all_books: list[Path] = list_all_book_files(series_tag)
        self.current_file: Optional[os.DirEntry] = None
        self.current_book: Optional[Doc] = None
        self.book_names_dict = self.generate_book_dict()

    def set_new_series(self, input_series: str):
        self.series_tag = input_series
        self.all_books = list_all_book_files(input_series)
        self.book_names_dict = self.generate_book_dict()

    def generate_book_dict(self) -> dict:
        return {index: book.name.split('.')[0] for index, book in enumerate(self.all_books) if index != 0}

    def select_book(self, book_index: int) -> None:
        self.current_file = self.all_books[book_index]
        self.current_book = self.__apply_nlp(self.current_file)
        print(f"Selected book → {self.current_file.name}")

    def set_book_example(self) -> None:
        book: Path = self.all_books[1]
        self.current_book = self.__apply_nlp(book)

    def __apply_nlp(self, input_book: Path) -> Doc:
        input_book_location = str(input_book)
        with open(input_book_location, encoding="utf8") as f:
            book_text = f.read()
            text_size = len(book_text)
            if text_size <= TEXT_SIZE:
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
        chunk_size = CHUNK_SIZE
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
        return displacy.render(book[:100], style="ent", jupyter=True, minify=True)

    def __get_book_entities(self) -> pd.DataFrame:
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
            return self._create_new_book_entity_table()
        return self._read_existing_book_entity_table()

    def __get_file_tag(self) -> str:
        return f"{self.current_file.name.split('.')[0]}.csv"

    def __existing_entity_file(self) -> bool:
        return Path(get_entities_file_path(self.series_tag), f"{self.__get_file_tag()}").exists()

    def _create_new_book_entity_table(self) -> pd.DataFrame:
        print("Book entity not found. Processing a new one...")
        book_entities: pd.DataFrame = self.__get_book_entities()
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