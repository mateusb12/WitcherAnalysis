import pandas as pd


def cleanup_df(input_df: pd.DataFrame) -> None:
    input_df["character"] = input_df["character"].str.replace(r'\(.*\)', "", regex=True)
    input_df["character_first_name"] = input_df["character"].apply(lambda x: x.split(" ", 1)[0])


def main():
    print("done")


if __name__ == "__main__":
    main()
