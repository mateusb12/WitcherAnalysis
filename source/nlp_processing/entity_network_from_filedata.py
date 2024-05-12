import pandas as pd

from nlp_processing.entity_analysis.text_processor import TextProcessor
from nlp_processing.model_loader import load_nlp_model


class EntityNetworkPipeline:
    def __init__(self):
        self.model = load_nlp_model()
        self.text_processor = TextProcessor(self.model)
        self.text_data: str = ""
        self.character_table: pd.DataFrame = pd.DataFrame()

    def setup(self, text_data: str, character_table: pd.DataFrame):
        self.text_data = text_data
        self.character_table = character_table

    def analyze_pipeline(self):
        pass


def main():
    pass


if __name__ == "__main__":
    main()
