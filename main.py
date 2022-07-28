# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import dataclasses
import os

import spacy
from spacy.lang import en as english

from path_reference.folder_reference import get_data_path

# NER = spacy.load('en_core_web_sm')
# print(type(NER))

print(spacy.__version__)

@dataclasses.dataclass
class BookAnalyser:
    # all_books: list[os.DirEntry] = None

    def __post_init__(self):
        self.NER: english = spacy.load('en_core_web_sm')
        self.all_books: list[os.DirEntry] = [book for book in os.scandir(get_data_path()) if '.txt' in book.name]



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
