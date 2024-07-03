import asyncio
import time

from Scraper.scraper import Scraper


async def main() -> None:
    start = time.time()
    url = "https://www.domstol.se/hogsta-domstolen/"
    driver_path = "/usr/bin/chromedriver"
    scraper = Scraper(url, driver_path)
    source = scraper.fetch_page_source()
    scraper.extract_pdf_urls(source)
    await scraper.download_latest_pdfs()
    end = time.time()
    print(end - start)


if __name__ == '__main__':
    asyncio.run(main())
