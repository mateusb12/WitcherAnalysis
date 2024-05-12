from io import StringIO

import pandas as pd


def load_csv_text_example() -> str:
    return ("book,character,character_first_name\nBaptism of Fire,Adalia,Adalia\nBaptism of Fire,Adela,Adela\n"
            "Baptism of Fire,Aen Saevherne,Aen\nBaptism of Fire,Aevenien,Aevenien\nBaptism of Fire,Aglaïs,Aglaïs\n"
            "Baptism of Fire,Albrich,Albrich\nBaptism of Fire,Amavet,Amavet\nBaptism of Fire,Angus Bri Cri,Angus\n"
            "Baptism of Fire,Anna Kameny,Anna\nBaptism of Fire,Anzelm Aubry,Anzelm")


def convert_string_to_dataframe(input_str: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(input_str))


def main():
    csv_text = load_csv_text_example()
    df = convert_string_to_dataframe(csv_text)
    print(df)


if __name__ == "__main__":
    main()
