import os
import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

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
        self.page_url: str = "https://www.reddit.com/login"
        self.saved_links = []

    def run(self):
        self.__load_website()
        self.__login_process()
        self.__load_saved_items_page()
        # self.collect_saved_items_links()
        # self.driver.close()

    def __load_website(self) -> None:
        self.driver.get(self.page_url)
        self.driver.implicitly_wait(1)

    def __login_process(self):
        username = os.getenv("REDDIT_USERNAME")
        password = os.getenv("REDDIT_PASSWORD")
        login_input_id = "loginUsername"
        login_element = self.driver.find_element(By.ID, login_input_id)
        login_element.send_keys(username)
        password_input_id = "loginPassword"
        password_element = self.driver.find_element(By.ID, password_input_id)
        password_element.send_keys(password)
        button_xpath = "/html/body/div/main/div[1]/div/div[2]/form/fieldset[5]/button"
        button_element = self.driver.find_element(By.XPATH, button_xpath)
        time.sleep(1)
        button_element.click()
        time.sleep(5)

    def __load_saved_items_page(self):
        username = os.getenv("REDDIT_USERNAME")
        saved_items_url = f"https://www.reddit.com/user/{username}/saved/"
        self.driver.get(saved_items_url)
        self.driver.implicitly_wait(1)

    def collect_saved_items_links(self):
        main_list = self.__get_main_list_element()
        for element in main_list:
            link = self.__get_link_from_single_element(element)
            self.saved_links.append(link)

    def __get_main_list_element(self):
        main_list_xpath = "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[2]/div[1]"
        main_list = self.driver.find_element(By.XPATH, main_list_xpath)
        return main_list.find_elements(By.XPATH, ".//*")

    def __get_link_from_single_element(self, element):
        primary_button = element.find_element(By.XPATH, ".//button[@data-click-id='share']")
        primary_button.click()

        sub_buttons_xpath = ".//button"
        sub_buttons = self.driver.find_elements(By.XPATH, sub_buttons_xpath)
        menuitem_buttons = [button for button in sub_buttons if button.get_attribute('role') == 'menuitem']
        first_menu_item_button = menuitem_buttons[0]
        first_menu_item_button.click()

        time.sleep(1)
        return pyperclip.paste()


def __main():
    rs = RedditScrapper()
    rs.run()


if __name__ == "__main__":
    __main()
