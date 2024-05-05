import re

from source.nlp_processing.entity_analysis.book_manager import BookManager
from source.nlp_processing.entity_analysis.entity_extractor import EntityExtractor
from source.nlp_processing.entity_analysis.entity_filter import EntityFilter
from source.nlp_processing.entity_analysis.relationship_creator import RelationshipCreator
from source.nlp_processing.model_loader import load_nlp_model


class BookAnalysisPipeline:
    def __init__(self, nlp_model, series_tag="harry_potter"):
        self.book_manager = BookManager(nlp_model, series_tag)
        self.entity_extractor = EntityExtractor()
        self.entity_filter = EntityFilter(series=series_tag)
        self.relationship_creator = RelationshipCreator()

    def run_pipeline(self, book_index: int):
        # Select and analyze the book
        book_name = self.book_manager.all_books[book_index].name
        book_title = re.search(r"\d+\s+(.*?)\.txt", book_name).group(1)
        print(f"1/5 Analyzing book '{book_title}'")
        self.book_manager.select_book(book_index)

        # Extract entities from the book
        print("2/5 Extracting entities")
        entities = self.book_manager.get_book_entities()

        # Set the entities dataframe for filtering
        print("3/5 Filtering entities")
        self.entity_filter.set_entity_df(entities)

        # Filter the entities and get the filtered dataframe
        print("4/5 Creating relationships")
        character_only_df = self.entity_filter.export_filtered_dataframe()

        # Aggregate the network and get the final dataframe
        print("5/5 Aggregating network")
        self.relationship_creator.set_entity_df(character_only_df)
        network_df = self.relationship_creator.aggregate_network()

        return network_df


def main():
    model = load_nlp_model()
    pipeline = BookAnalysisPipeline(model)
    network_df = pipeline.run_pipeline(1)
    return network_df


if __name__ == "__main__":
    main()
