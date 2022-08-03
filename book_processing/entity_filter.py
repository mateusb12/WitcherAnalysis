from pathlib import Path

import pandas as pd

from book_processing.entity_extractor import get_entities_df
from path_reference.folder_reference import get_data_path


def __cast_to_str(list_obj: list) -> str:
    return str(list_obj)


def __convert_to_list(input_str: str) -> list[str]:
    if isinstance(input_str, list):
        input_str = __cast_to_str(input_str)
    forbidden_characters = ["[", "'", "]"]
    for c in forbidden_characters:
        input_str = input_str.replace(c, "")
    return input_str.split(", ")


def _filter_entity_df(entity_list: str, characters_df: pd.DataFrame):
    entity_pot = __convert_to_list(entity_list)
    full_names = characters_df["character"].tolist()
    first_names = characters_df["character_first_name"].tolist()
    return [x for x in entity_pot if x in first_names or x in full_names]


class EntityFilter:
    def __init__(self):
        self.entity_df = None
        self.characters_df = pd.read_csv(Path(get_data_path(), "characters.csv"))

    def set_entity_df(self, input_df: pd.DataFrame) -> None:
        self.entity_df = input_df.copy()

    def __filter_character_only_entities(self) -> None:
        self.entity_df["character_entities"] = self.entity_df["entities"].apply(
            lambda x: _filter_entity_df(x, self.characters_df))

    def __filter_empty_entities(self) -> None:
        self.entity_df = self.entity_df[self.entity_df["character_entities"].map(len) > 0]

    def __filter_double_names(self) -> None:
        # Swap "Geralt of Rivia" with "Geralt"
        self.entity_df["character_entities"] = self.entity_df["character_entities"].apply(
            lambda x: [item.split()[0] for item in x])

    def __delete_entity_column(self) -> None:
        del self.entity_df["entities"]

    def __filter_pipeline(self) -> None:
        self.__filter_character_only_entities()
        self.__filter_empty_entities()
        self.__filter_double_names()
        self.__delete_entity_column()

    def export_filtered_dataframe(self) -> pd.DataFrame:
        self.__filter_pipeline()
        return self.entity_df


def get_entity_df() -> pd.DataFrame:
    ea = EntityFilter()
    return ea.export_filtered_dataframe()


def __main():
    ea = EntityFilter()
    aux = ea.entity_df
    print("done")


if __name__ == "__main__":
    __main()
