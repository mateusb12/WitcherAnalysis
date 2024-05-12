import re

import pandas as pd

from source.data.cache.cache_loader import existing_relationship_cache, existing_entity_cache
from source.nlp_processing.entity_analysis.book_manager import BookManager
from source.nlp_processing.entity_analysis.entity_extractor import EntityExtractor
from source.nlp_processing.entity_analysis.entity_filter import EntityFilter
from source.nlp_processing.entity_analysis.relationship_creator import RelationshipCreator
from source.nlp_processing.model_loader import load_nlp_model


class BooKEntityNetworkBuilder:
    def __init__(self, nlp_model, series_tag="harry_potter"):
        self.book_manager = BookManager(nlp_model, series_tag)
        self.entity_extractor = EntityExtractor()
        self.entity_filter = EntityFilter(series=series_tag)
        self.relationship_creator = RelationshipCreator()
        self.book_title: str = ""
        self.book_index: int = 0

    def run_pipeline(self, book_index: int):
        book_name = self.book_manager.all_books[book_index].name
        self.book_index = book_index
        self.book_title = re.search(r"\d+\s+(.*?)\.txt", book_name).group(1)
        return self.get_relationship_table(self.book_title)

    def get_relationship_table(self, book_title: str) -> pd.DataFrame:
        existing_cache = existing_relationship_cache(f"{book_title}.csv")
        if existing_cache:
            return pd.read_csv(str(existing_cache))
        print("Relationship table cache not found. Processing it...")
        character_only_df: pd.DataFrame = self.get_filtered_entities(book_title)
        self.relationship_creator.set_entity_df(character_only_df)
        network_df: pd.DataFrame = self.relationship_creator.aggregate_network()
        return network_df

    def get_filtered_entities(self, book_title: str) -> pd.DataFrame:
        existing_cache = existing_entity_cache(f"{book_title}.csv")
        if existing_cache:
            return pd.read_csv(str(existing_cache))
        print("Entity table cache not found. Processing it...")
        self.book_manager.select_book(self.book_index)
        entities: pd.DataFrame = self.book_manager.get_book_entities()
        self.entity_filter.set_entity_df(entities)
        character_only_df: pd.DataFrame = self.entity_filter.export_filtered_dataframe()
        character_only_df.to_csv(str(existing_cache), index=False)
        return character_only_df


def main():
    model = load_nlp_model()
    pipeline = BooKEntityNetworkBuilder(model)
    network_df = pipeline.run_pipeline(1)
    return network_df


if __name__ == "__main__":
    main()
