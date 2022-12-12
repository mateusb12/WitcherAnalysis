from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from path_reference.folder_reference import get_driver_path, get_data_path


class TwilightScrapper:
    def __init__(self):
        s = Service(str(get_driver_path()))
        self.driver = webdriver.Firefox(service=s)
        self.page_url: str = "https://twilightsaga.fandom.com/wiki/Category:Twilight_Saga_characters"
        self.category_links = ["https://twilightsaga.fandom.com/wiki/Category:Twilight",
                               "https://twilightsaga.fandom.com/wiki/Category:New_Moon",
                               "https://twilightsaga.fandom.com/wiki/Category:Eclipse",
                               "https://twilightsaga.fandom.com/wiki/Category:Breaking_Dawn"]
        self.character_links = []
        self.book_links = {}
        self.characters = []

    def run(self):
        self.__load_website()
        self.__scrap_characters()
        self.__convert_to_table()
        self.driver.close()

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

    def __scrap_characters(self):
        for link in self.category_links:
            book_name = link.split(":")[-1]
            self.driver.get(link)
            main_div = self.driver.find_element(By.ID, "content")
            table_div = main_div.find_element(By.CLASS_NAME, "category-page__members")
            sub_tables = table_div.find_elements(By.CLASS_NAME, "category-page__members-wrapper")[1:]
            for sub_table in sub_tables:
                sub_table_ul = sub_table.find_element(By.TAG_NAME, "ul")
                characters = sub_table_ul.text.split("\n")
                for character in characters:
                    character_tag = {"book": book_name, "character": character}
                    self.characters.append(character_tag)

    def __convert_to_table(self):
        df = pd.DataFrame(self.characters)
        df["character_first_name"] = df["character"].apply(lambda x: x.split(" ", 1)[0])
        df.to_csv(Path(get_data_path(), "books_characters", "twilight_characters.csv"),
                  index=False, encoding="utf-8")


def __main():
    hps = TwilightScrapper()
    hps.run()
    return


if __name__ == '__main__':
    __main()
