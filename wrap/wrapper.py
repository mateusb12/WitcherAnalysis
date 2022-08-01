import pandas as pd

from nlp.entity_extractor import BookAnalyser
from nlp.entity_filter import EntityFilter
from nlp.relationship_creator import RelationshipCreator


class Wrapper:
    def __init__(self):
        self.book_analyser = BookAnalyser()
        self.entity_filter = EntityFilter()
        self.relationship_creator = RelationshipCreator()
        self.df: pd.DataFrame = pd.DataFrame()
        self.relationship_df: pd.DataFrame = pd.DataFrame()

    def set_book(self, book_number: int):
        self.book_analyser.select_book(book_number)

    def book_pipeline(self):
        entity_df = self.book_analyser.get_book_entity_df()
        self.entity_filter.set_entity_df(entity_df)
        self.df = self.entity_filter.export_filtered_dataframe()
        self.relationship_creator.set_entity_df(self.df)
        self.relationship_df = self.relationship_creator.aggregate_network()


def __main():
    w = Wrapper()
    w.book_pipeline()
