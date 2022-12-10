from pathlib import Path

from path_reference.folder_reference import get_book_graphs_path


def existing_analysis(book_name: str):
    """Check whether the book_name.html exists in book_graphs folder"""
    return Path(get_book_graphs_path(), f"{book_name}.html").exists()


def __main():
    print(existing_analysis("2 The Sword of Destiny"))


if __name__ == '__main__':
    __main()
