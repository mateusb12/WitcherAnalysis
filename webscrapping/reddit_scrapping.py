import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from path_reference.folder_reference import get_driver_path
from dotenv import load_dotenv


def find_text_inputs(element, input_list):
    # Get all child elements of the current element
    children_elements = element.find_elements(By.XPATH, './*')

    for child in children_elements:
        # If the child is an input element with type 'text' or 'password', add it to the list
        if child.tag_name.lower() == 'input':
            input_type = child.get_attribute('type')
            if input_type in ['text', 'password']:
                input_list.append(child)

        # Recursively call the function for the current child
        find_text_inputs(child, input_list)


class RedditScrapper:
    def __init__(self):
        load_dotenv()
        s = Service(str(get_driver_path()))
        self.driver = webdriver.Firefox(service=s)
        self.page_url: str = "https://www.reddit.com/"
        self.book_links = {}
        self.characters = []

    def run(self):
        self.__load_website()
        self.__login_process()
        # self.driver.close()

    def __load_website(self) -> None:
        self.driver.get(self.page_url)
        self.driver.implicitly_wait(1)
        # self.__close_cookies_window()

    def __login_process(self):
        self.__press_first_login_button()
        self.driver.implicitly_wait(3)
        self.__type_login_information()
        self.__press_second_login_button()

    def __press_first_login_button(self):
        xpath = ("/html/body/shreddit-app/reddit-header-large/reddit-header-action-items/header/nav/div[3]/span[3]/"
                 "faceplate-tracker/faceplate-tooltip/a/span/span")
        login_button = self.driver.find_element(By.XPATH, xpath)
        login_button.click()

    def __type_login_information(self):
        email_xpath = '//body/shreddit-app[1]/div[1]/div[1]'
        password_xpath = '//*[@id="left-sidebar-container"]'
        email_input = self.driver.find_element(By.XPATH, email_xpath)
        password_input = self.driver.find_element(By.XPATH, password_xpath)
        login = os.environ["REDDIT_LOGIN"]
        password = os.environ["REDDIT_PASSWORD"]
        email_input.send_keys(login)
        password_input.send_keys(password)

    def __press_second_login_button(self):
        login_button_xpath = '/html/body/div/main/div[1]/div/div/form/fieldset[4]/button'
        login_button = self.driver.find_element(By.XPATH, login_button_xpath)
        login_button.click()


def __main():
    rs = RedditScrapper()
    rs.run()


if __name__ == "__main__":
    __main()
