import pandas as pd

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
    return final_df


def __main():
    get_importance(get_importance_example())


if __name__ == "__main__":
    __main()
    print("Done")
