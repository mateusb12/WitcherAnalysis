from pathlib import Path

import pandas as pd

from data.df_cleanup import cleanup_df
from nlp.books import get_entities_df
from path_reference.folder_reference import get_data_path


def filter_entity_df(entity_list: list[str], characters_df: pd.DataFrame):
    first_names = [x.lower() for x in characters_df["character_first_name"].tolist()]
    full_names = [x.lower() for x in characters_df["character"].tolist()]
    lower_entity_list = [x.lower() for x in entity_list]
    return [entity for entity in lower_entity_list
            if entity in first_names
            or entity in full_names]


class EntityAnalyser:
    def __init__(self):
        self.entity_df = get_entities_df()
        self.characters_df = pd.read_csv(Path(get_data_path(), "characters.csv"))
        cleanup_df(self.characters_df)

    def filter_entities(self) -> None:
        # Filter all entities that are not in the characters list
        self.entity_df["character_entities"] = self.entity_df["entities"].apply(
            lambda x: filter_entity_df(x, self.characters_df))
        # Filter all empty entities
        self.entity_df = self.entity_df[self.entity_df["character_entities"].map(len) > 0]
        # Swap "Geralt of Rivia" with "Geralt"
        self.entity_df["character_entities"] = self.entity_df["character_entities"].apply(
            lambda x: [item.split()[0] for item in x])


def __main():
    ea = EntityAnalyser()
    ea.filter_entities()
    aux = ea.entity_df
    print("done")


if __name__ == "__main__":
    __main()
