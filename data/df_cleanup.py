from pathlib import Path

import pandas as pd

from path_reference.folder_reference import get_data_path


# class CharactersCleanup:
#     def __init__(self):
#         self.df = pd.read_csv(Path(get_data_path(), "characters.csv"))
#
#     def remove_parenthesis(self):
#         self.df["character"] = self.df["character"].str.replace("\(.*\)", "")
#
#     def generate_first_name(self):
#         self.df["character_first_name"] = self.df["character"].apply(lambda x: x.split(" ", 1)[0])

def cleanup_df(input_df: pd.DataFrame) -> None:
    # input_df["character"] = input_df["character"].str.replace("\(.*\)", "")
    input_df["character"] = input_df["character"].str.replace(r'\(.*\)', "", regex=True)
    input_df["character_first_name"] = input_df["character"].apply(lambda x: x.split(" ", 1)[0])


def __main():
    ccc = CharactersCleanup()
    ccc.remove_parenthesis()
    ccc.generate_first_name()
    aux = ccc.df
    print(aux)


if __name__ == "__main__":
    __main()
