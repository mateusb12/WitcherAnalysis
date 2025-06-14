import re
import tkinter as tk
from tkinter import ttk
from typing import List

from source.visual_interfaces.utils import get_book_folders, get_book_names
from source.scripts.existing_graphs import retrieve_book
from source.scripts.runner import Runner


class BookSelector:
    def __init__(self, window_size: tuple[int, int] = (500, 500)):
        self.wrapper = Runner()
        self.root = tk.Tk()
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.first_dropdown, self.second_dropdown, self.query_button = None, None, None
        self.first_dropdown_selected_option, self.second_dropdown_selected_option = tk.StringVar(), tk.StringVar()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the coordinates of the top-left corner of the window
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        # Set the geometry of the window
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.run()

    def run(self):
        self.instantiate_first_dropdown()
        self.instantiate_second_dropdown()
        self.instantiate_query_button()
        self.root.mainloop()

    def instantiate_first_dropdown(self):
        options = get_book_folders()
        first_option = options[0]
        self.first_dropdown_selected_option.set(first_option)
        self.first_dropdown = ttk.OptionMenu(self.root, self.first_dropdown_selected_option, first_option, *options,
                                             command=self.execute_first_dropdown)
        style = ttk.Style()
        style.theme_use("clam")
        self.first_dropdown.pack_configure(side="top", pady=0.07 * self.window_height)

    def instantiate_second_dropdown(self):
        first_dropdown_option = self.first_dropdown_selected_option.get()
        options = get_book_names(first_dropdown_option)
        first_option = options[0]
        self.second_dropdown_selected_option.set(first_option)
        self.second_dropdown = ttk.OptionMenu(self.root, self.second_dropdown_selected_option, first_option, *options,
                                              command=self.execute_second_dropdown)
        self.second_dropdown.pack_configure(side="top", pady=0.01 * self.window_height)

    def update_second_dropdown_options(self):
        first_dropdown_option = self.first_dropdown_selected_option.get()
        options = get_book_names(first_dropdown_option)
        self.second_dropdown["menu"].delete(0, "end")
        for option in options:
            self.second_dropdown["menu"].add_command(label=option,
                                                     command=lambda
                                                         value=option: self.second_dropdown_selected_option.set(value))
        self.second_dropdown_selected_option.set(options[0])

    def instantiate_query_button(self):
        self.query_button = tk.Button(self.root, text="Query", command=self.execute_query_button)
        self.query_button.pack_configure(side="top", pady=0.07 * self.window_height)
        self.query_button["background"] = "blue"
        self.query_button["foreground"] = "white"
        self.query_button["font"] = ("Helvetica", 14, "bold")
        self.query_button["relief"] = "groove"
        self.query_button["highlightbackground"] = "black"

    def execute_query_button(self):
        raw_series = self.first_dropdown_selected_option.get()
        chosen_series = raw_series.lower().replace(" books", "").replace(" ", "_" if " " in raw_series else "")
        self.wrapper.book_analyser.set_series(chosen_series)
        chosen_book = self.second_dropdown_selected_option.get()
        book_match = re.match(r"\d+", chosen_book)
        if not book_match:
            raise ValueError("Invalid book option")
        book_number = int(book_match.group())
        existing_book = retrieve_book(chosen_book)
        if not existing_book:
            new_wrapper = Runner(series=chosen_series)
            new_wrapper.load_book(book_number)
            new_wrapper.process_entities()
            new_wrapper.plot()

    def execute_first_dropdown(self, value):
        self.first_dropdown_selected_option.set(value)
        self.update_second_dropdown_options()

    def execute_second_dropdown(self, value):
        self.second_dropdown_selected_option.set(value)


def __main():
    example = BookSelector()


if __name__ == "__main__":
    __main()
