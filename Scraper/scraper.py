import re
import time

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from helpers.split_utils import split_and_divide


class Scraper:
    def __init__(self, url, driver_path):
        self.url = url
        self.driver_path = driver_path
        self.pdf_urls = []
        self.pdf_base_url = "https://www.domstol.se"

    def fetch_page_source(self):
        # Initialize the webdriver with the specified path
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(service=Service(executable_path=self.driver_path), options=options)

        driver.get(self.url)
        # Wait until the element is present and click the link
        avgoranden_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/hogsta-domstolen/avgoranden/']"))
        )
        avgoranden_link.click()
        time.sleep(2)

        element = driver.find_element(By.XPATH,
                                      "//h2[@class='heading__selector--search-header hide--small-down' and "
                                      "@data-testid='HeadingSelector']")
        text = element.get_attribute('innerText')
        # Extract the relevant text from the HTML code
        max_clicks = split_and_divide(text)

        print(max_clicks)

        # Load all content by clicking 'Show More' button until it disappears
        for _ in range(2):
            try:
                show_more = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@title='Visa mer']"))
                )
                ActionChains(driver).move_to_element(show_more).click(show_more).perform()
                # WebDriverWait(driver, 10).until(
                #     EC.staleness_of(show_more)  # check if the element referenced by the show_more variable is no
                #     # longer present in the DOM.
                # )
            except:
                print('break')
                break

        page_source = driver.page_source
        driver.quit()
        return page_source

    def extract_pdf_urls(self, page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        for link in soup.find_all('a', class_='search-result-item', href=True):
            href = link['href']
            title = link.get('title', '')
            if 'Mål:' in title:
                print(link.parent)
                self.pdf_urls.append(self.pdf_base_url+href)
