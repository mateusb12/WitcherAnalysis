from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from path_reference.folder_reference import get_driver_path


class WitcherScrapper:
    def __init__(self):
        s = Service(str(get_driver_path()))
        self.driver = webdriver.Firefox(service=s)
        self.page_url: str = "https://witcher.fandom.com/wiki/Category:Characters_in_the_stories"

    def load_website(self):
        self.driver.get(self.page_url)
        self.close_cookies_window()

    def close_cookies_window(self):
        self.driver.find_element(By.XPATH, "/html/body/div[7]/div/div/div[2]/div[2]").click()

    def get_book_list(self):
        raw_categories = self.driver.find_elements(By.CLASS_NAME, "category-page__member-link")
        return [book.get_attribute("href") for book in raw_categories]

    def get_book_content(self, book_link):
        self.driver.get(book_link)
        character_content = self.driver.find_elements(By.CLASS_NAME, "category-page__member-link")
        return [item.text for item in character_content]

    def pipeline(self):
        book_links = self.get_book_list()
        for book_link in book_links:
            yield self.get_book_content(book_link)


def __main():
    ws = WitcherScrapper()
    ws.pipeline()
    # ws.get_book_list()


if __name__ == "__main__":
    __main()
