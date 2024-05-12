import pandas as pd
from spacy.tokens import Doc

from nlp_processing.entity_analysis.entity_extractor import EntityExtractor
from nlp_processing.entity_analysis.relationship_creator import RelationshipCreator
from nlp_processing.entity_analysis.text_processor import TextProcessor
from nlp_processing.model_loader import load_nlp_model
from utils.entity_utils import filter_entity_df


class EntityNetworkPipeline:
    def __init__(self):
        self.model = load_nlp_model()
        self.text_processor = TextProcessor(self.model)
        self.entity_extractor = EntityExtractor()
        self.relationship_creator = RelationshipCreator()
        self.text_data: str = ""
        self.character_table: pd.DataFrame = pd.DataFrame()

    def setup(self, text_data: str, character_table: pd.DataFrame):
        self.text_data = text_data
        self.character_table = character_table

    def analyze_pipeline(self):
        entity_df = self.get_booK_entity_dataframe()
        character_only_df = self.filter_entity_dataframe(entity_df)
        self.relationship_creator.set_entity_df(character_only_df)
        relationship_df = self.relationship_creator.aggregate_network()
        pass

    def get_booK_entity_dataframe(self) -> pd.DataFrame:
        entity_data: Doc = self.text_processor.analyze_book_from_text_data(self.text_data)
        self.entity_extractor.setup_entity_data(entity_data)
        return self.entity_extractor.extract_book_entities()

    def filter_entity_dataframe(self, entity_df: pd.DataFrame) -> pd.DataFrame:
        # Filter the entity dataframe using the character table
        entity_df['entities'] = entity_df['entities'].apply(filter_entity_df, characters_df=self.character_table)
        return entity_df


def main():
    pass


if __name__ == "__main__":
    main()
