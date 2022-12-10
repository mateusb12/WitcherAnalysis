import tkinter as tk
from tkinter import ttk
from typing import List


class BookSelector:
    def __init__(self, window_size: tuple[int, int] = (500, 500)):
        self.root = tk.Tk()
        self.root.geometry(f"{window_size[0]}x{window_size[1]}")
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.dropdown = None
        self.instance_pipeline()

    def instance_pipeline(self):
        self.instantiate_dropdown()
        self.root.mainloop()

    def instantiate_dropdown(self):
        options = ["1", "2", "3", "4", "5"]
        self.dropdown = ttk.OptionMenu(self.root, tk.StringVar(), *options, command=self.execute_dropdown)
        style = ttk.Style()
        style.theme_use("clam")
        self.dropdown.pack_configure(side="top", pady=0.07*self.window_height)

    @staticmethod
    def execute_dropdown(value):
        print(value)
        # print(self.dropdown["text"])


def __main():
    example = BookSelector()


if __name__ == "__main__":
    __main()
