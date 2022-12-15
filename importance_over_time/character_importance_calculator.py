import sys
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from fix_non_reachable_path import fix_non_reachable_path
from path_reference.folder_reference import get_book_importance_path
from wrap.wrapper import Wrapper


def get_importance_example(series_name: str) -> list[str]:
    if series_name.lower() == "witcher":
        return ["Geralt", "Ciri", "Yennefer", "Dandelion", "Vesemir"]
    else:
        return [""]


class CharacterImportanceOverTime:
    def __init__(self, series_name: str = "witcher"):
        self.series_name = series_name
        self.series_importance_folder = Path()
        self.amount_of_books = 0

    def run(self, amount_of_books: int = 3):
        self.amount_of_books = amount_of_books
        existing_folder = self.__check_existing_importance_folder()
        if not existing_folder:
            self.__create_importance_folder()
        self.__create_importance_dataframes()

    def __check_existing_importance_folder(self) -> bool:
        books_importance_folder = get_book_importance_path()
        self.series_importance_folder = Path(books_importance_folder, f"{self.series_name}_books_importance")
        return Path(self.series_importance_folder).is_dir()

    def __create_importance_folder(self):
        Path(self.series_importance_folder).mkdir(parents=True, exist_ok=True)
        Path(self.series_importance_folder, "__init__.py").touch()

    def __get_existing_csv_files(self) -> list[Path]:
        return [f for f in Path(self.series_importance_folder).iterdir() if f.suffix == ".csv"]

    def __get_missing_csv_files(self, existing_csv_files: list[Path]) -> list[int]:
        max_book_index = int(existing_csv_files[-1].name.split(" ")[0])
        return list(range(max_book_index + 1, self.amount_of_books + 1))

    def __create_importance_dataframes(self):
        existing_csv_files = self.__get_existing_csv_files()
        missing_books = self.__get_missing_csv_files(existing_csv_files)
        if not missing_books:
            return
        w = Wrapper(series=self.series_name)
        for i in missing_books:
            w.set_book(i)
            book_name = w.book_name
            csv_output = Path(self.series_importance_folder, f"{book_name}_importance.csv")
            if Path(csv_output).is_file():
                continue
            relationship_df = w.book_pipeline()
            relationship_df.to_csv(csv_output, index=True, encoding="utf-8")


def get_importance_df(series: str = "witcher", char_list: list[str] = None) -> pd.DataFrame:
    if char_list is None:
        char_list = ["Geralt", "Ciri", "Yennefer", "Dandelion", "Vesemir"]
    books_importance_folder = get_book_importance_path()
    series_importance_folder = Path(books_importance_folder, f"{series}_books_importance")
    files = [f for f in Path(series_importance_folder).iterdir() if f.is_file() and f.suffix == ".csv"]
    book_pot = []
    amount = 3
    for file in files:
        file_index = int(file.stem.split(" ")[0])
        if file_index > amount:
            break
        relationship_df = pd.read_csv(file, encoding="utf-8")
        relationship_df = relationship_df.rename(columns={relationship_df.columns[0]: "Character Name",
                                                          relationship_df.columns[1]: "Importance"})
        relationship_df["Book Index"] = file_index
        book_pot.append(relationship_df)
    final_df = pd.concat(book_pot)
    final_df = final_df[final_df["Character Name"].isin(char_list)]
    return final_df


def plot_importance(importance_df: pd.DataFrame):
    """Dataframe is in this format:
    Character Name, Importance, Book Index
    Geralt, 0.5, 1
    Cirilla, 0.3, 1
    Yennefer, 0.2, 2"""
    plt.figure(figsize=(15, 8))
    maximum_index = int(importance_df["Book Index"].max()) + 1
    plt.xticks(range(1, maximum_index))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x * 100), ',')))
    plt.rcParams.update({'font.size': 12})
    plt.title("Importance over time")
    plt.xlabel("Books")
    plt.ylabel("Importance (%)")
    plt.rcParams['lines.linewidth'] = 2
    plt.grid(which='major', color='#666666', linewidth=1.0)

    names = importance_df['Character Name']
    importance = importance_df['Importance']
    book_index = importance_df['Book Index']
    unique_names = set(names)

    for name in unique_names:
        x = book_index[names == name]
        y = importance[names == name]
        plt.plot(x, y, label=name, linestyle='-', marker='o', markersize=9)

    plt.legend(unique_names)
    plt.show()


def plot_series_importance(series_name: str):
    characters = get_importance_example(series_name)
    cio = CharacterImportanceOverTime(series_name)
    cio.run(amount_of_books=3)
    importance_df = get_importance_df(series=series_name, char_list=characters)
    plot_importance(importance_df)
    return


fix_non_reachable_path()


def __main():
    plot_series_importance("witcher")
    # print(is_path_reference_folder_reachable())


if __name__ == "__main__":
    __main()
