from nlp.entity_extractor import BookAnalyser


class Wrapper:
    def __init__(self):
        self.book_analyser = BookAnalyser()

    def set_book(self, book_number: int):
        self.book_analyser.select_book(book_number)



