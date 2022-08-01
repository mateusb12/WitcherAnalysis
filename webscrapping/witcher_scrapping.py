from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from path_reference.folder_reference import get_driver_path, get_data_path


class WitcherScrapper:
    def __init__(self):
        s = Service(str(get_driver_path()))
        self.driver = webdriver.Firefox(service=s)
        self.page_url: str = "https://witcher.fandom.com/wiki/Category:Characters_in_the_stories"

    def __load_website(self) -> None:
        self.driver.get(self.page_url)
        self.driver.implicitly_wait(1)
        self.__close_cookies_window()

    def __close_cookies_window(self) -> None:
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, ".NN0_TB_DIsNmMHgJWgT7U")
            button.click()
        except NoSuchElementException:
            print("Could not close cookies window")

    def __get_book_list(self) -> dict:
        raw_categories = self.driver.find_elements(By.CLASS_NAME, "category-page__member-link")
        return {self.__fix_book_name(book.get_attribute("title")): book.get_attribute("href")
                for book in raw_categories}

    def __get_book_content(self, book_link) -> list[str]:
        self.driver.get(book_link)
        character_content = self.driver.find_elements(By.CLASS_NAME, "category-page__member-link")
        return [item.text for item in character_content]

    @staticmethod
    def __fix_book_name(input_string) -> str:
        sentence = input_string.split(":")[-1].split(" ")[:-1]
        return ' '.join(sentence).replace("\"", "")

    def __get_book_table(self) -> list[dict]:
        self.__load_website()
        book_table: dict = self.__get_book_list()
        character_pot = []
        for book_name, book_link in book_table.items():
            current_book_characters: list = self.__get_book_content(book_link)
            character_pot.extend({"book": book_name, "character": character}
                                 for character in current_book_characters)
        return character_pot

    def export_dataframe(self) -> None:
        df = pd.DataFrame(self.__get_book_table())
        df["character_first_name"] = df["character"].apply(lambda x: x.split(" ", 1)[0])
        df.to_csv(Path(get_data_path(), "characters.csv"), index=False)
        self.driver.close()


def __main():
    ws = WitcherScrapper()
    ws.export_dataframe()
    print("done")


if __name__ == "__main__":
    __main()
