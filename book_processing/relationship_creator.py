import numpy as np
import pandas as pd

from book_processing.entity_extractor import BookAnalyser
from book_processing.entity_filter import EntityFilter, get_witcher_filtered_df


class RelationshipCreator:
    def __init__(self):
        self.entity_df = None
        self.window_size: int = 5

    def set_entity_df(self, input_df: pd.DataFrame) -> None:
        self.entity_df = input_df

    @staticmethod
    def __remove_duplicates(input_list: list[str]) -> list[str]:
        maximum_size = len(input_list) - 1
        unique_list = []
        for index, item in enumerate(input_list):
            current_item = item
            next_item = input_list[min(index + 1, maximum_size)]
            if current_item != next_item:
                unique_list.append(current_item)
        return unique_list

    @staticmethod
    def __get_relationship_list(unique_list: list[str]) -> list:
        if len(unique_list) <= 1:
            return []
        relationship_list = []
        for index, item in enumerate(unique_list):
            source = item
            target = unique_list[min(index + 1, len(unique_list) - 1)]
            if source != target:
                relationship_list.append({"source": source, "target": target})
        return relationship_list

    @staticmethod
    def __bidirectional_sort(input_dataframe: pd.DataFrame) -> pd.DataFrame:
        """ Sort cases where a→b and b→a"""
        sorted_table = np.sort(input_dataframe.values, axis=1)
        cols = input_dataframe.columns
        return pd.DataFrame(sorted_table, columns=cols)

    def __loop_window(self) -> pd.DataFrame:
        maximum_df_index = len(self.entity_df)
        relationship_pot = []

        for i in range(self.entity_df.index[-1]):
            window_end = min(i + self.window_size, maximum_df_index)
            window = self.entity_df.loc[i:i + window_end]
            window_characters = sum(window.character_entities, [])
            unique_characters = self.__remove_duplicates(window_characters)
            relationships = self.__get_relationship_list(unique_characters)
            relationship_pot.extend(relationships)
        return pd.DataFrame(relationship_pot)

    def aggregate_network(self, window_size: int = 5) -> pd.DataFrame:
        self.window_size = window_size
        raw_df = self.__loop_window()
        network_df = self.__bidirectional_sort(raw_df)
        network_df["value"] = 1
        return network_df.groupby(["source", "target"], sort=False, as_index=False).sum()


def get_network_df() -> pd.DataFrame:
    rc = RelationshipCreator()
    return rc.aggregate_network()


def __main():
    rc = RelationshipCreator()
    entity_df = get_witcher_filtered_df()
    rc.set_entity_df(entity_df)
    relationship_dict = rc.aggregate_network()
    return 0


if __name__ == "__main__":
    __main()
