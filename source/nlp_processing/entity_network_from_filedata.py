import pandas as pd
from spacy.tokens import Doc

from nlp_processing.entity_analysis.entity_extractor import EntityExtractor
from nlp_processing.entity_analysis.text_processor import TextProcessor
from nlp_processing.model_loader import load_nlp_model


class EntityNetworkPipeline:
    def __init__(self):
        self.model = load_nlp_model()
        self.text_processor = TextProcessor(self.model)
        self.entity_extractor = EntityExtractor()
        self.text_data: str = ""
        self.character_table: pd.DataFrame = pd.DataFrame()

    def setup(self, text_data: str, character_table: pd.DataFrame):
        self.text_data = text_data
        self.character_table = character_table

    def analyze_pipeline(self):
        pass

    def get_booK_entity_dataframe(self):
        entity_data: Doc = self.text_processor.analyze_book_from_text_data(self.text_data)
        self.entity_extractor.setup_entity_data(entity_data)
        entity_df: pd.DataFrame = self.entity_extractor.extract_book_entities()
        return entity_df


def main():
    pass


if __name__ == "__main__":
    main()
