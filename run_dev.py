from Scraper.scraper import Scraper

if __name__ == '__main__':
    url = "https://www.domstol.se/hogsta-domstolen/"
    driver_path = "/usr/bin/chromedriver"
    scraper = Scraper(url, driver_path)
    source=scraper.fetch_page_source()
    scraper.extract_pdf_urls(source)
    print(scraper.pdf_urls)
