import json
import time
from pathlib import Path

from spacy.tokens import Doc

from path_reference.folder_reference import get_cache_path, get_nlp_cache_path
from utils.entity_utils import cache_file_exists, save_cache_file

CHUNK_SIZE = 500000
TEXT_SIZE = 1000000


class TextProcessor:
    def __init__(self, nlp):
        self.nlp = nlp

    def load_cache_file_content(self, file_location: Path):
        filename = file_location.name.split('.')[0]
        cache_file_path = Path(get_nlp_cache_path(), f"{filename}.bin")
        return Doc(self.nlp.vocab).from_disk(cache_file_path)

    def analyze_book(self, input_book: Path) -> Doc:
        if cache_file_exists(input_book):
            print(f'- -             Cache file located. Loading [{input_book.name}]')
            return self.load_cache_file_content(input_book)

        with open(input_book, encoding="utf8") as f:
            print(f'- -             Cache file not found. Processing [{input_book.name}]')
            nlp_start = time.time()
            doc = self.__apply_nlp_to_book(f)
        save_cache_file(input_book, doc)
        print(f"Book processed in {round(time.time() - nlp_start, 2)} seconds")
        return doc

    def analyze_book_from_text_data(self, text_data: str) -> Doc:
        """Process text data from a string rather than a file, without involving caching."""
        print(f'Processing text data directly.')
        nlp_start = time.time()
        text_size = len(text_data)
        if text_size <= TEXT_SIZE:
            doc = self.nlp(text_data)
        else:
            print("Large text detected. Splitting...")
            doc = self.__process_large_file(text_data)
        print(f"Text data processed in {round(time.time() - nlp_start, 2)} seconds")
        return doc

    def __apply_nlp_to_book(self, f):
        book_text = f.read()
        text_size = len(book_text)
        if text_size <= TEXT_SIZE:
            doc = self.nlp(book_text)
        else:
            print("Big file detected. Splitting...")
            doc = self.__process_large_file(book_text)
        return doc

    def __process_large_file(self, file_content: str) -> Doc:
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
