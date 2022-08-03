import pandas as pd
from matplotlib import pyplot as plt

from wrap.wrapper import Wrapper


def get_importance_example() -> list[str]:
    return ["Geralt", "Ciri", "Yennefer", "Dandelion", "Vesemir"]


def get_importance(char_list: list[str]) -> pd.DataFrame:
    w = Wrapper()
    amount = 3
    book_pot = []
    for i in range(1, amount + 1):
        w.set_book(i)
        book_pot.append(w.book_pipeline())
    final_df = pd.DataFrame.from_records(book_pot)
    final_df = final_df[char_list]
    final_df.plot()
    final_df.index += 1
    return final_df


def plot_importance(importance_df: pd.DataFrame):
    plt.figure(figsize=(15, 8))
    plt.xticks(range(1, len(importance_df.index) + 1))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x * 100), ',')))
    plt.rcParams.update({'font.size': 12})
    plt.title("Importance over time")
    plt.xlabel("Books")
    plt.ylabel("Importance (%)")
    plt.rcParams['lines.linewidth'] = 2
    plt.grid(which='major', color='#666666', linewidth=1.0)
    plt.legend(importance_df.columns)
    plt.plot(importance_df, linestyle='-', marker='o', markersize=9)


def __main():
    get_importance(get_importance_example())


if __name__ == "__main__":
    __main()
    print("Done")
