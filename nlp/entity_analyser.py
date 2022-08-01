from pathlib import Path

import pandas as pd

from nlp.entity_extractor import get_entities_df
from path_reference.folder_reference import get_data_path


def __convert_to_list(input_str: str) -> list[str]:
    forbidden_characters = ["[", "'", "]"]
    for c in forbidden_characters:
        input_str = input_str.replace(c, "")
    return input_str.split(", ")


def filter_entity_df(entity_list: str, characters_df: pd.DataFrame):
    entity_pot = __convert_to_list(entity_list)
    full_names = [x.lower() for x in characters_df["character"].tolist()]
    first_names = [x.lower() for x in characters_df["character_first_name"].tolist()]
    return [x for x in entity_pot
            if x.lower() in first_names
            or x.lower() in full_names]


class EntityAnalyser:
    def __init__(self):
        self.entity_df = get_entities_df()
        self.characters_df = pd.read_csv(Path(get_data_path(), "characters.csv"))
        # cleanup_df(self.characters_df)

    def __filter_character_entities(self) -> None:
        self.entity_df["character_entities"] = self.entity_df["entities"].apply(
            lambda x: filter_entity_df(x, self.characters_df))

    def __filter_empty_entities(self) -> None:
        self.entity_df = self.entity_df[self.entity_df["character_entities"].map(len) > 0]

    def __filter_double_names(self) -> None:
        # Swap "Geralt of Rivia" with "Geralt"
        self.entity_df["character_entities"] = self.entity_df["character_entities"].apply(
            lambda x: [item.split()[0] for item in x])

    def __filter_pipeline(self) -> None:
        self.__filter_character_entities()
        self.__filter_empty_entities()
        self.__filter_double_names()

    def export_dataframe(self) -> pd.DataFrame:
        self.__filter_pipeline()
        return self.entity_df


def __main():
    ea = EntityAnalyser()
    ea.__filter_pipeline()
    aux = ea.entity_df
    print("done")


if __name__ == "__main__":
    __main()
