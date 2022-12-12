import spacy

from path_reference.folder_reference import get_books_path


def flatten_lines(line_pot: list[str]):
    new_lines = []
    for line in line_pot:
        if line.startswith('Page | '):
            continue
        if line == "\n":
            continue
        new_lines.append(line.replace("\n", ""))
    return " ".join(new_lines)


def split_chunks(flattened_lines: str):
    """This function splits the text into chunks of 1000 characters"""
    fixed_size = 1000000
    if len(flattened_lines) < fixed_size:
        return [flattened_lines]
    else:
        return [flattened_lines[i:i + fixed_size] for i in range(0, len(flattened_lines), fixed_size)]


class BookFixer:
    def __init__(self, folder_name: str):
        self.folder_name = folder_name
        self.nlp = spacy.load("en_core_web_sm")

    def fix_harry_potter_books(self):
        book_folder = get_books_path() / f'{self.folder_name}_books'
        for index, book in enumerate(book_folder.iterdir()):
            print(f"Fixing {book} (#{index+1})")
            with open(book, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            single_line = flatten_lines(lines)
            chunks = split_chunks(single_line)
            sentences = self.analyze_multiple_chunks(chunks)
            with open(book, 'w', encoding='utf-8') as f:
                for new_line in sentences:
                    f.write(new_line + '\n')
            continue
        return

    def analyze_single_chunk(self, flattened_lines: str):
        doc = self.nlp(flattened_lines)
        return [sent.text for sent in doc.sents]

    def analyze_multiple_chunks(self, flattened_lines_group: list[str]):
        nested = [self.analyze_single_chunk(flattened_lines) for flattened_lines in flattened_lines_group]
        return [item for sublist in nested for item in sublist]


def __main():
    bf = BookFixer('harry_potter')
    bf.fix_harry_potter_books()


if __name__ == '__main__':
    __main()
