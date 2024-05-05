from pathlib import Path

from path_reference.folder_reference import get_books_path


def get_book_folders():
    raw_books_names = [f for f in get_books_path().iterdir() if f.is_dir()]
    book_type_names = [str(f).split("\\")[-1] for f in raw_books_names]
    return [book_type_name.replace("_", " ").title() for book_type_name in book_type_names]


def get_book_names(folder_name: str):
    real_folder_name = folder_name.lower().replace(" ", "_")
    if "_books" not in real_folder_name:
        real_folder_name += "_books"
    raw_books_names = [f for f in get_books_path().iterdir() if f.is_dir()]
    folder_path = [f for f in raw_books_names if str(f).split("\\")[-1] == real_folder_name]
    folder_content = [f for f in folder_path[0].iterdir() if f.is_file()]
    book_names = [str(f).split("\\")[-1] for f in folder_content]
    adjusted_book_names = [book_name for book_name in book_names if ".txt" in book_name]
    return [book_name.replace(".txt", "") for book_name in adjusted_book_names]


def __main():
    print(get_book_names("Harry Potter"))


if __name__ == '__main__':
    __main()
