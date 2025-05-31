import pandas as pd

from nlp_processing.entity_analysis.entity_filter import get_witcher_filtered_df
from utils.relationship_utils import bidirectional_sort, get_source_target_relationship_list, remove_string_duplicates


class RelationshipCreator:
    def __init__(self):
        self.entity_df = None
        self.window_size: int = 5

    def set_entity_df(self, input_df: pd.DataFrame) -> None:
        if "entities" not in input_df.columns:
            raise ValueError("The input DataFrame must contain an 'entities' column.")
        self.entity_df = input_df

    def __extract_relationships_from_entities(self) -> pd.DataFrame:
        """Iterates over the entity dataframe and creates relationships between entities within a given window size"""
        maximum_df_index = len(self.entity_df)
        relationship_pot = []

        for i in range(self.entity_df.index[-1]):
            window_end = min(i + self.window_size, maximum_df_index)
            window = self.entity_df.loc[i:i + window_end]
            window_characters = sum(window.entities, [])
            unique_characters = remove_string_duplicates(window_characters)
            relationships = get_source_target_relationship_list(unique_characters)
            relationship_pot.extend(relationships)
        return pd.DataFrame(relationship_pot)

    def aggregate_network(self, window_size: int = 5) -> pd.DataFrame:
        """Aggregates the relationships created by __extract_relationships_from_entities()
        Returns a dataframe containing the relationships between entities in the input dataframe.
        The window size can be optionally specified."""
        self.window_size = window_size
        raw_df = self.__extract_relationships_from_entities()
        network_df = bidirectional_sort(raw_df)
        network_df["value"] = 1
        return network_df.groupby(["source", "target"], sort=False, as_index=False).sum()


def get_network_df() -> pd.DataFrame:
    rc = RelationshipCreator()
    entity_df = get_witcher_filtered_df()
    rc.set_entity_df(entity_df)
    return rc.aggregate_network()


def __main():
    network_df = get_network_df()
    return 0


if __name__ == "__main__":
    __main()
