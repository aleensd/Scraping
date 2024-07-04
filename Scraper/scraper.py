import asyncio
import json
import time
import aiohttp
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from config import Config
from helpers.app_logger import get_logger
from helpers.check_element_utils import check_exists_by_class_name
from helpers.split_utils import split_and_divide

logger = get_logger(__name__)


class Scraper:
    def __init__(self):
        self.url = Config().url
        self.driver_path = Config().driver_path
        self.pdf_urls = []
        self.pdf_base_url = Config().pdf_base_url
        # Initialize the webdriver with the specified path
        self.options = Options()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        # self.options.add_argument('--incognito')
        self.options.add_argument('start-maximized')
        # self.options.add_argument('--window-size=1920,1080')
        # Download options
        self.options.add_experimental_option('prefs', {
            "download.default_directory": Config().download_default_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })
        self.driver = None
        self.init_driver()

    def init_driver(self):
        if self.driver is None:
            self.driver = webdriver.Chrome(service=Service(executable_path=self.driver_path), options=self.options)
            logger.debug('driver initialized')

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.debug('driver quit')

    def apply_filters(self):
        # Click the dropdown to expand it
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "AvgörandetypFilter_dropdown_trigger"))
        ).click()
        logger.debug('Avgorandetype filter clicked!')

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[@title='Prejudikat']"))
        ).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//label[@title='Begäran om förhandsavgörande']"))
        ).click()

    def fetch_page_source(self) -> str:
        self.init_driver()
        self.driver.get(self.url)
        time.sleep(2)
        self.apply_filters()
        logger.debug('filters applied')
        time.sleep(2)

        element = self.driver.find_element(By.XPATH,
                                           "//h2[@class='heading__selector--search-header hide--small-down' and "
                                           "@data-testid='HeadingSelector']")
        text = element.get_attribute('innerText')
        max_clicks = split_and_divide(text)
        logger.info('Number of loops to extract all pdf urls: %s', max_clicks)

        # Load all content by clicking 'Show More' button until it disappears
        for _ in range(max_clicks):
            try:
                show_more = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@title='Visa mer']"))
                )
                ActionChains(self.driver).move_to_element(show_more).click(show_more).perform()
            except Exception as e:
                logger.debug('show more button not found: %s', e)
                break

        page_source = self.driver.page_source
        self.quit_driver()
        return page_source

    def extract_pdf_urls(self, page_source) -> None:
        soup = BeautifulSoup(page_source, 'html.parser')
        for link in soup.find_all('a', class_='search-result-item', attrs={'data-testid': 'SearchResultItem'},
                                  href=True):
            href = link['href']
            self.pdf_urls.append(self.pdf_base_url + href)

    @staticmethod
    async def get_pdf_content(session, pdf_url) -> str:
        try:
            async with session.get(pdf_url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Failed to get PDF content from {pdf_url}: {e}")

    async def extract_pdf_metadata(self, session, pdf_url) -> dict:
        content = await self.get_pdf_content(session, pdf_url)
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('span', class_='article__sub-title', attrs={'data-testid': 'subTitle'}).text.strip()
            return {
                'title': title,
                'url': pdf_url,
                'malnummer': self.extract_value_list_content(soup, 'Målnummer'),
                'benamning': self.extract_value_list_content(soup, 'Benämning'),
                'lagrum': self.extract_value_list_content(soup, 'Lagrum', 'li'),
                'rattsfall': self.extract_value_list_content(soup, 'Rättsfall', 'li'),
                'sokord': self.extract_value_list_content(soup, 'Sökord', 'link')

            }
        return None

    async def save_metadata_to_json(self) -> None:
        async with aiohttp.ClientSession() as session:
            logger.info('Saving %s pdfs metadata to json', len(self.pdf_urls))

            # tasks = [self.extract_pdf_metadata(session, url) for url in self.pdf_urls]
            # results = await asyncio.gather(*tasks)
            # self.metadata_list = [result for result in results if result]
            metadata_list = []
            for url in self.pdf_urls:
                metadata = await self.extract_pdf_metadata(session, url)
                metadata_list.append(metadata)

            df = pd.DataFrame(metadata_list)
            df.to_csv('metadata.csv', index=False)
            # df.to_json('metadata.json', orient='records', lines=True, force_ascii=False)
            with open('metadata.json', 'w', encoding='utf-8') as f:
                json.dump(metadata_list, f, ensure_ascii=False)

    async def download_latest_pdfs(self) -> None:
        self.init_driver()
        try:
            tasks = [self.download_pdf(url) for url in self.pdf_urls[:10]]
            await asyncio.gather(*tasks)
        finally:
            self.quit_driver()

    async def download_pdf(self, pdf_url) -> None:
        try:
            self.driver.get(pdf_url)
            if check_exists_by_class_name(self.driver, "link-block__link"):
                link_block = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "link-block__link"))
                )
                link_block.click()
        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")

    @staticmethod
    def extract_value_list_content(soup, title, type="text") -> str | list[str] | None:
        anchor_div = soup.find('div', class_='anchor', id=title)
        if anchor_div:
            parent_div = anchor_div.find_parent('div', class_='preheading--small')
            if type == 'text':
                div = parent_div.find_next_sibling('div', class_='value-list', attrs={'data-testid': 'ValueList'})
                return div.text.strip() if div else None
            elif type == 'li':
                ul_element = parent_div.find_next_sibling('ul', class_='value-list value-list--unordered',
                                                          attrs={'data-testid': 'ValueListUnordered'})
                return [li.text.strip() for li in
                        ul_element.find_all('li', class_='value-list__item')] if ul_element else None
            elif type == 'link':
                div = parent_div.find_next_sibling('div', class_='value-list', attrs={'data-testid': 'LinkList'})
                return [link['href'] for link in
                        div.find_all('a', class_='link', attrs={'data-testid': 'Link'})] if div else None
        else:
            return None
