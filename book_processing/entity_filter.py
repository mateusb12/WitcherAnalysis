from pathlib import Path

import pandas as pd

from path_reference.folder_reference import get_data_path, get_books_entities_path, get_book_characters_path, \
    get_books_path


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
    def __init__(self, series: str = "witcher"):
        self.entity_df = None
        character_path = Path(get_data_path(), "books_characters", f"{series}_characters.csv")
        if existing_file := Path(character_path).is_file():
            self.characters_df = pd.read_csv(character_path)
        else:
            raise FileNotFoundError(f"File {character_path} does not exist")

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


def __get_witcher_book_example() -> Path:
    return Path(get_books_path(), "witcher_books", "1 The Last Wish.txt")


def __get_harry_potter_book_example() -> Path:
    return Path(get_books_path(), "harry_potter_books", "1 The Philosopher's Stone.txt")


def __get_witcher_entity_example() -> Path:
    return Path(get_books_entities_path(), "witcher_books_entities", "1 The Last Wish.csv")


def __get_harry_potter_entity_example() -> Path:
    return Path(get_books_entities_path(), "harry_potter_books_entities", "1 The Philosopher's Stone.csv")


def get_filtered_entity_df() -> pd.DataFrame:
    ea = EntityFilter()
    book_path = __get_witcher_entity_example()
    entity_df = pd.read_csv(book_path, encoding="utf-8")
    ea.set_entity_df(entity_df)
    return ea.export_filtered_dataframe()


def __main():
    aux = get_filtered_entity_df()
    return 0


if __name__ == "__main__":
    __main()
