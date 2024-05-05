from pathlib import Path

import pandas as pd

from source.path_reference.folder_reference import get_data_path, get_books_path, get_books_entities_path, \
    get_character_table_path
from source.utils.entity_utils import filter_entity_df


class EntityFilter:
    """This function is used to filter the entity dataframe, only including character entities.
    The characters.csv file is loaded from the book_characters folder.
    It contains the main characters of the book, and should be obtained through web scrapping the book wiki page.
    There are already some examples in the folder, for the series 'The Witcher', 'Harry Potter' and 'Twilight'. """
    def __init__(self, series: str = "witcher"):
        self.entity_df = None
        character_path = Path(get_character_table_path(), f"{series}_characters.csv")
        if existing_file := Path(character_path).is_file():
            self.characters_df = pd.read_csv(character_path)
        else:
            raise FileNotFoundError(f"File {character_path} does not exist")

    def set_entity_df(self, input_df: pd.DataFrame) -> None:
        self.entity_df = input_df.copy()

    def __filter_character_only_entities(self) -> None:
        self.entity_df["character_entities"] = self.entity_df["entities"].apply(
            lambda x: filter_entity_df(x, self.characters_df))

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


def get_witcher_filtered_df() -> pd.DataFrame:
    ea = EntityFilter(series="witcher")
    book_path = __get_witcher_entity_example()
    entity_df = pd.read_csv(book_path, encoding="utf-8")
    ea.set_entity_df(entity_df)
    return ea.export_filtered_dataframe()


def get_harry_potter_filtered_df() -> pd.DataFrame:
    ea = EntityFilter(series="harry_potter")
    book_path = __get_harry_potter_entity_example()
    entity_df = pd.read_csv(book_path, encoding="utf-8")
    ea.set_entity_df(entity_df)
    return ea.export_filtered_dataframe()


def __main():
    aux = get_harry_potter_filtered_df()
    return 0


if __name__ == "__main__":
    __main()
