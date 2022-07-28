from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from path_reference.folder_reference import get_driver_path

s = Service(str(get_driver_path()))
driver = webdriver.Firefox(service=s)
print(driver)
