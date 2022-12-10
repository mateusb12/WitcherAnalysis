import tkinter as tk
from tkinter import ttk
from typing import List

from gui.utils import get_book_folders, get_book_names


class BookSelector:
    def __init__(self, window_size: tuple[int, int] = (500, 500)):
        self.root = tk.Tk()
        self.root.geometry(f"{window_size[0]}x{window_size[1]}")
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.first_dropdown, self.second_dropdown = None, None
        self.first_dropdown_selected_option, self.second_dropdown_selected_option = tk.StringVar(), tk.StringVar()
        self.run()

    def run(self):
        self.instantiate_first_dropdown()
        self.instantiate_second_dropdown()
        self.root.mainloop()

    def instantiate_first_dropdown(self):
        options = get_book_folders()
        first_option = options[0]
        self.first_dropdown_selected_option.set(first_option)
        self.first_dropdown = ttk.OptionMenu(self.root, self.first_dropdown_selected_option, first_option, *options,
                                             command=self.execute_dropdown)
        style = ttk.Style()
        style.theme_use("clam")
        self.first_dropdown.pack_configure(side="top", pady=0.07 * self.window_height)

    def instantiate_second_dropdown(self):
        first_dropdown_option = self.first_dropdown_selected_option.get()
        options = get_book_names(first_dropdown_option)
        first_option = options[0]
        self.second_dropdown_selected_option.set(first_option)
        self.second_dropdown = ttk.OptionMenu(self.root, self.second_dropdown_selected_option, first_option, *options)
        self.second_dropdown.pack_configure(side="top", pady=0.14 * self.window_height)

    def update_second_dropdown_options(self):
        first_dropdown_option = self.first_dropdown_selected_option.get()
        options = get_book_names(first_dropdown_option)
        self.second_dropdown["menu"].delete(0, "end")
        for option in options:
            self.second_dropdown["menu"].add_command(label=option,
                                                     command=lambda value: self.second_dropdown_selected_option.set(
                                                         value))
        self.second_dropdown_selected_option.set(options[0])

    def execute_dropdown(self, value):
        print(value)
        self.first_dropdown_selected_option.set(value)
        self.update_second_dropdown_options()
        # print(self.dropdown["text"])


def __main():
    example = BookSelector()


if __name__ == "__main__":
    __main()
