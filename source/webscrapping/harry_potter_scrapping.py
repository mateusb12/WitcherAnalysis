from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from path_reference.folder_reference import get_driver_path, get_data_path


class HarryPotterScrapper:
    def __init__(self):
        s = Service(str(get_driver_path()))
        self.driver = webdriver.Firefox(service=s)
        self.page_url: str = "https://harrypotter.fandom.com/wiki/Category:Character_indexes"
        self.book_links = {}
        self.characters = []

    def run(self):
        self.__load_website()
        self.__get_character_pages_links()
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

    def __get_character_pages_links(self):
        list_xpath = "/html/body/div[4]/div[3]/div[3]/main/div[3]/div[1]/div[3]/div/ul"
        ul_list = self.driver.find_elements(By.XPATH, list_xpath)[0]
        book_names = [book_name.split(" (")[0] for book_name in ul_list.text.split("\n")]
        a_elements = ul_list.find_elements(By.TAG_NAME, "a")
        book_links = [a_element.get_attribute("href") for a_element in a_elements]
        for book_name, book_link in zip(book_names, book_links):
            self.book_links[book_name] = book_link

    def __scrap_characters(self):
        for book_name, book_link in self.book_links.items():
            self.driver.get(book_link)
            table_list = self.driver.find_elements(By.CLASS_NAME, "article-table")
            for table in table_list:
                table_characters = table.text.split("\n")
                for character in table_characters:
                    self.characters.append({"book": book_name, "character": character})

    def __convert_to_table(self):
        df = pd.DataFrame(self.characters)
        df["character_first_name"] = df["character"].apply(lambda x: x.split(" ", 1)[0])
        df.to_csv(Path(get_data_path(), "books_characters", "harry_potter_characters.csv"),
                  index=False, encoding="utf-8")


def __main():
    hps = HarryPotterScrapper()
    hps.run()
    return


if __name__ == '__main__':
    __main()
