import os
from pathlib import Path
from typing import Optional

from spacy import displacy
from spacy.tokens import Doc

from source.nlp_processing.entity_extractor import EntityExtractor
from source.nlp_processing.model_loader import load_nlp_model
from source.nlp_processing.text_processor import TextProcessor
from source.utils.entity_utils import list_all_book_files


class BookManager:
    def __init__(self, nlp_model, series_tag: str = "harry_potter"):
        self.text_processor = TextProcessor(nlp_model)
        self.entity_extractor = EntityExtractor()
        self.series_tag = series_tag
        self.all_books: list[Path] = list_all_book_files(series_tag)
        self.current_file: Optional[os.DirEntry] = None
        self.current_book: Optional[Doc] = None
        self.book_names_dict = self.generate_book_dict()

    def set_series(self, input_series: str):
        self.series_tag = input_series
        self.all_books = list_all_book_files(input_series)
        self.book_names_dict = self.generate_book_dict()

    def select_book(self, book_index: int):
        self.current_file = self.all_books[book_index]
        self.current_book = self.text_processor.analyze_book(self.current_file)
        self.entity_extractor.set_information(book=self.current_book, file=self.current_file, series=self.series_tag)
        print(f"Selected book → {self.current_file.name}")

    def generate_book_dict(self) -> dict:
        return {index: book.name.split('.')[0] for index, book in enumerate(self.all_books) if index != 0}

    def set_book_example(self) -> None:
        book: Path = self.all_books[1]
        self.current_book = self.text_processor.analyze_book(book)

    def print_book(self) -> str:
        book = self.current_book
        return displacy.render(book[:100], style="ent", jupyter=True, minify=True)

    def get_book_entities(self):
        return self.entity_extractor.get_book_entity_table()


def main():
    model = load_nlp_model()
    book_manager = BookManager(model)
    book_manager.select_book(1)
    book_manager.print_book()
    aux = book_manager.get_book_entities()
    return 0


if __name__ == "__main__":
    main()
