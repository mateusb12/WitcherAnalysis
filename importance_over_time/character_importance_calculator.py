from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from path_reference.folder_reference import get_book_importance_path
from wrap.wrapper import Wrapper


def get_importance_example() -> list[str]:
    return ["Geralt", "Ciri", "Yennefer", "Dandelion", "Vesemir"]


def create_importance_dataframes(series: str = "witcher"):
    books_importance_folder = get_book_importance_path()
    series_importance_folder = Path(books_importance_folder, f"{series}_books_importance")
    if not Path(series_importance_folder).is_dir():
        Path(series_importance_folder).mkdir(parents=True, exist_ok=True)
        Path(series_importance_folder, "__init__.py").touch()
    w = Wrapper(series=series)
    amount = 3
    for i in range(1, amount + 1):
        w.set_book(i)
        book_name = w.book_name
        csv_output = Path(series_importance_folder, f"{book_name}_importance.csv")
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
    # final_df.index += 1
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


def __main():
    characters = get_importance_example()
    # create_importance_dataframes(series="witcher")
    importance_df = get_importance_df(series="witcher", char_list=characters)
    plot_importance(importance_df)
    return


if __name__ == "__main__":
    __main()
    print("Done")
