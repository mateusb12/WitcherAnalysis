import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from utils.time_utils import convert_time_format

ELEMENT_AMOUNT = 3392


class WebElementSearcher:
    def __init__(self, element_list: List[WebElement]):
        self.element_list = element_list
        self.elements_found_so_far = []
        self.attempts = 0
        self.visited_elements = set()
        self.start_time = None

    def find_text_inputs(self):
        self.start_time = time.time()
        for element in self.element_list:
            self._recursive_search(element)

    def _recursive_search(self, element: WebElement):
        if element.id in self.visited_elements:
            return
        self.attempts += 1
        right_now = time.time()
        time_so_far = right_now - self.start_time
        velocity = self.attempts / time_so_far if time_so_far != 0 else 0
        rounded_velocity = round(velocity, 2)
        remaining_elements = ELEMENT_AMOUNT - len(self.elements_found_so_far)
        remaining_time = remaining_elements / velocity if velocity != 0 else 0
        formatted_remaining_time = convert_time_format(time.strftime('%H:%M:%S', time.gmtime(remaining_time)))
        eta = right_now + remaining_time
        formatted_eta = time.strftime('%H:%M:%S', time.gmtime(eta))
        print(f"Attempt #{self.attempts}, Velocity: {rounded_velocity} elements/s,"
              f" Remaining time: {formatted_remaining_time},"
              f" ETA: {formatted_eta}")
        # Get all child elements of the current element
        children_elements = element.find_elements(By.XPATH, './*')

        for child in children_elements:
            # If the child is an input element with type 'text' or 'password', add it to the list
            if child.tag_name.lower() == 'input':
                input_type = child.get_attribute('type')
                if input_type in ['text', 'password', 'email']:
                    self.elements_found_so_far.append(child)

            # Recursively call the function for the current child
            self._recursive_search(child)
