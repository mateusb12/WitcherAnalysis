import pandas as pd

from nlp.entity_analyser import get_entity_df


class RelationshipCreator:
    def __init__(self):
        self.entity_df = get_entity_df()

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

    def loop_window(self) -> pd.DataFrame:
        windows_size = 5
        maximum_df_index = len(self.entity_df)
        relationship_pot = []

        for i in range(self.entity_df.index[-1]):
            window_end = min(i + windows_size, maximum_df_index)
            window = self.entity_df.loc[i:i + window_end]
            window_characters = sum(window.character_entities, [])
            unique_characters = self.__remove_duplicates(window_characters)
            relationships = self.__get_relationship_list(unique_characters)
            relationship_pot.extend(relationships)
        return pd.DataFrame(relationship_pot)


def __main():
    rc = RelationshipCreator()
    rc.loop_window()


if __name__ == "__main__":
    __main()
