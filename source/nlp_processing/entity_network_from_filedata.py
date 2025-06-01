import pandas as pd
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from spacy.tokens import Doc

from nlp_processing.entity_analysis.entity_extractor import EntityExtractor
from nlp_processing.entity_analysis.node_plot import NodePlot
from nlp_processing.entity_analysis.relationship_creator import RelationshipBuilder
from nlp_processing.entity_analysis.text_processor import TextProcessor
from nlp_processing.model_loader import load_nlp_model
from utils.entity_utils import filter_entity_df


def save_progress(progress, session_key):
    # Save progress in your cache (if needed)
    cache.set(f'upload_progress_{session_key}', progress)

    # Get the channel layer
    channel_layer = get_channel_layer()

    # Send the progress update to the group based on the session key
    async_to_sync(channel_layer.group_send)(
        f'progress_{session_key}',
        {
            'type': 'progress_update',  # This calls the "progress_update" method in the consumer
            'progress': progress,
        }
    )


class EntityNetworkPipeline:
    def __init__(self, progress_callback=None):
        self.model = load_nlp_model()
        self.text_processor = TextProcessor(self.model)
        self.entity_extractor = EntityExtractor()
        self.relationship_creator = RelationshipBuilder()
        self.node_plot = NodePlot()
        self.text_data: str = ""
        self.character_table: pd.DataFrame = pd.DataFrame()
        self.book_filename: str = ""
        self.progress_callback = progress_callback

    def setup(self, text_data: str, character_table: pd.DataFrame, book_filename: str):
        self.text_data = text_data
        self.character_table = character_table
        self.book_filename = book_filename

    def analyze_pipeline(self):
        entity_df = self.get_booK_entity_dataframe()
        character_only_df = self.filter_entity_dataframe(entity_df)
        self.relationship_creator.set_entity_df(character_only_df)
        relationship_df = self.relationship_creator.aggregate_network()
        self.node_plot.set_network_df(relationship_df)
        self.node_plot.plot(book_name=self.book_filename)

    def get_booK_entity_dataframe(self) -> pd.DataFrame:
        entity_data: Doc = self.text_processor.analyze_book_from_text_data(self.text_data)
        sentences = list(entity_data.sents)
        total = len(sentences)
        processed_spans = []

        for idx, sent in enumerate(sentences):
            processed_spans.append(sent)
            # Report progress every 10 sentences (or adjust as needed)
            if self.progress_callback and idx % 10 == 0:
                progress = (idx + 1) / total
                self.progress_callback(progress)

        # Reconstruct the Doc object with processed sentences
        entity_data = Doc(entity_data.vocab, words=[token.text for sent in processed_spans for token in sent])
        self.entity_extractor.setup_entity_data(entity_data)
        return self.entity_extractor.extract_book_entities()

    def filter_entity_dataframe(self, entity_df: pd.DataFrame) -> pd.DataFrame:
        entity_df['entities'] = entity_df['entities'].apply(filter_entity_df, characters_df=self.character_table)
        return entity_df


def main():
    pass


if __name__ == "__main__":
    main()
