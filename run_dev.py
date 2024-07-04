import asyncio
import time

from Scraper.scraper import Scraper


async def main() -> None:
    start = time.time()
    scraper = Scraper()
    source = scraper.fetch_page_source()
    scraper.extract_pdf_urls(source)
    await  scraper.save_metadata_to_json()
    await scraper.download_latest_pdfs()
    end = time.time()
    print(end - start)


if __name__ == '__main__':
    asyncio.run(main())
